from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.models.vehicle import VehicleType
from app.models.checklist import ChecklistTemplate
from app.schemas.p2h import (
    ChecklistItemResponse,
    ChecklistItemCreate,  # Pastikan sudah ada di schemas
    P2HReportSubmit,
    P2HReportResponse,
    P2HReportListResponse
)
from app.services.p2h_service import p2h_service
from app.dependencies import get_current_user, require_role
from app.utils.response import base_response

router = APIRouter()

# --- ENDPOINT BARU: TAMBAH PERTANYAAN DARI FE ---

@router.post("/checklist", status_code=status.HTTP_201_CREATED)
async def add_checklist_item(
    item_data: ChecklistItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Endpoint untuk menambah pertanyaan baru langsung dari UI Front-End.
    Mendukung sistem tagging vehicle_tags dan applicable_shifts.
    """
    new_item = ChecklistTemplate(
        item_name=item_data.question_text,  # Mapping ke kolom item_name di DB
        section_name=item_data.section_name,
        vehicle_tags=item_data.vehicle_tags,      # Simpan list tipe kendaraan
        applicable_shifts=item_data.applicable_shifts, # Simpan list shift
        options=item_data.options,
        item_order=item_data.item_order,
        is_active=True
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return base_response(
        message="Pertanyaan baru berhasil ditambahkan ke database",
        payload={
            "id": str(new_item.id),
            "question_text": new_item.item_name,
            "vehicle_tags": new_item.vehicle_tags
        }
    )

# --- ENDPOINT EKSISTING (TIDAK DIHAPUS) ---

@router.get("/checklist/{vehicle_type}")
async def get_checklist(
    vehicle_type: str, # Menggunakan str agar bisa fleksibel dengan tagging
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get checklist items yang ter-tag untuk tipe kendaraan tertentu.
    """
    # Mencari item yang kolom vehicle_tags-nya mengandung vehicle_type
    checklist_items = db.query(ChecklistTemplate).filter(
        ChecklistTemplate.vehicle_tags.any(vehicle_type),
        ChecklistTemplate.is_active == True
    ).order_by(
        ChecklistTemplate.section_name,
        ChecklistTemplate.item_order
    ).all()
    
    payload = [ChecklistItemResponse.model_validate(item).model_dump() for item in checklist_items]
    
    return base_response(
        message=f"Checklist untuk tipe {vehicle_type} berhasil diambil",
        payload=payload
    )

@router.get("/vehicle/{vehicle_id}/status")
async def get_vehicle_p2h_status(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        p2h_status = p2h_service.get_vehicle_p2h_status(db, vehicle_id)
        return base_response(
            message="Status P2H kendaraan berhasil diperiksa",
            payload=p2h_status
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_p2h(
    submission: P2HReportSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        report = await p2h_service.submit_p2h(db, current_user, submission)
        db.refresh(report)
        payload = P2HReportResponse.model_validate(report).model_dump()
        return base_response(
            message="Laporan P2H berhasil disubmit",
            payload=payload,
            status_code=201
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports")
async def get_p2h_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.p2h import P2HReport
    reports = db.query(P2HReport).order_by(
        P2HReport.submission_date.desc(),
        P2HReport.submission_time.desc()
    ).offset(skip).limit(limit).all()
    
    payload = [P2HReportListResponse.model_validate(r).model_dump() for r in reports]
    return base_response(message="Daftar laporan P2H berhasil diambil", payload=payload)

@router.get("/reports/{report_id}")
async def get_p2h_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.p2h import P2HReport
    report = db.query(P2HReport).filter(P2HReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Laporan P2H tidak ditemukan")
    
    payload = P2HReportResponse.model_validate(report).model_dump()
    return base_response(message="Detail laporan P2H berhasil ditemukan", payload=payload)