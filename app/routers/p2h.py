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
from datetime import datetime, time

router = APIRouter()

# --- ENDPOINT: MENDAPATKAN SHIFT SAAT INI ---
@router.get("/current-shift")
async def get_current_shift():
    """
    Endpoint untuk menentukan shift berdasarkan waktu sekarang.
    Shift 1: 07:00 - 15:00
    Shift 2: 15:00 - 23:00
    Shift 3: 23:00 - 07:00
    """
    current_time = datetime.now().time()
    
    shift_1_start = time(7, 0)   # 07:00
    shift_1_end = time(15, 0)    # 15:00
    shift_2_start = time(15, 0)  # 15:00
    shift_2_end = time(23, 0)    # 23:00
    
    if shift_1_start <= current_time < shift_1_end:
        shift_num = 1
        shift = "shift_1"
        shift_name = "Shift 1"
        time_range = "07:00 - 15:00"
        tolerance_start = "06:30"
    elif shift_2_start <= current_time < shift_2_end:
        shift_num = 2
        shift = "shift_2"
        shift_name = "Shift 2"
        time_range = "15:00 - 23:00"
        tolerance_start = "14:30"
    else:
        shift_num = 3
        shift = "shift_3"
        shift_name = "Shift 3"
        time_range = "23:00 - 07:00"
        tolerance_start = "22:30"
    
    return base_response(
        message="Shift saat ini berhasil dideteksi",
        payload={
            "current_shift": shift_num,
            "current_time": current_time.strftime("%H:%M:%S"),
            "shift_info": {
                "name": shift_name,
                "time_range": time_range,
                "tolerance_start": tolerance_start
            }
        }
    )

# --- ENDPOINT BARU: TAMBAH PERTANYAAN DARI FE ---

@router.get("/checklist-items")
async def get_all_checklist_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint untuk mendapatkan semua checklist items (pertanyaan P2H).
    Digunakan oleh frontend untuk filter berdasarkan vehicle_tags.
    """
    items = db.query(ChecklistTemplate).filter(
        ChecklistTemplate.is_active == True
    ).order_by(ChecklistTemplate.item_order).all()
    
    payload = [ChecklistItemResponse.model_validate(item).model_dump(mode='json') for item in items]
    
    return base_response(
        message="Semua checklist items berhasil diambil",
        payload=payload
    )

@router.post("/checklist-items", status_code=status.HTTP_201_CREATED)
async def add_checklist_item_to_items(
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

@router.get("/checklist")
async def get_checklist_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint untuk mendapatkan semua checklist items yang aktif.
    Digunakan oleh frontend untuk menampilkan pertanyaan-pertanyaan yang tersedia.
    """
    items = db.query(ChecklistTemplate).filter(
        ChecklistTemplate.is_active == True
    ).order_by(
        ChecklistTemplate.section_name,
        ChecklistTemplate.item_order
    ).all()
    
    payload = [ChecklistItemResponse.model_validate(item).model_dump(mode='json') for item in items]
    
    return base_response(
        message="Semua checklist items berhasil diambil",
        payload=payload
    )

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

@router.delete("/checklist-items/{checklist_id}", status_code=status.HTTP_200_OK)
async def delete_checklist_item(
    checklist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Endpoint untuk menghapus (soft delete) pertanyaan dari UI Front-End.
    """
    item = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    
    # Soft delete - set is_active to False
    item.is_active = False
    db.commit()
    
    return base_response(
        message="Pertanyaan berhasil dihapus",
        payload={"id": str(item.id)}
    )

@router.delete("/checklist/{checklist_id}", status_code=status.HTTP_200_OK)
async def delete_checklist_item_alt(
    checklist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Alias endpoint untuk DELETE /checklist-items/{id}.
    """
    item = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    
    # Soft delete - set is_active to False
    item.is_active = False
    db.commit()
    
    return base_response(
        message="Pertanyaan berhasil dihapus",
        payload={"id": str(item.id)}
    )

@router.put("/checklist-items/{checklist_id}", status_code=status.HTTP_200_OK)
async def update_checklist_item(
    checklist_id: UUID,
    item_data: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Endpoint untuk mengupdate pertanyaan yang sudah ada.
    """
    item = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    
    # Update fields
    item.item_name = item_data.question_text
    item.section_name = item_data.section_name
    item.vehicle_tags = item_data.vehicle_tags
    item.applicable_shifts = item_data.applicable_shifts
    item.options = item_data.options
    item.item_order = item_data.item_order
    
    db.commit()
    db.refresh(item)
    
    payload = ChecklistItemResponse.model_validate(item).model_dump(mode='json')
    return base_response(
        message="Pertanyaan berhasil diupdate",
        payload=payload
    )

@router.put("/checklist/{checklist_id}", status_code=status.HTTP_200_OK)
async def update_checklist_item_alt(
    checklist_id: UUID,
    item_data: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.superadmin, UserRole.admin))
):
    """
    Alias endpoint untuk PUT /checklist-items/{id}.
    """
    item = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    
    # Update fields
    item.item_name = item_data.question_text
    item.section_name = item_data.section_name
    item.vehicle_tags = item_data.vehicle_tags
    item.applicable_shifts = item_data.applicable_shifts
    item.options = item_data.options
    item.item_order = item_data.item_order
    
    db.commit()
    db.refresh(item)
    
    payload = ChecklistItemResponse.model_validate(item).model_dump(mode='json')
    return base_response(
        message="Pertanyaan berhasil diupdate",
        payload=payload
    )

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
    
    payload = [ChecklistItemResponse.model_validate(item).model_dump(mode='json') for item in checklist_items]
    
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
        payload = P2HReportResponse.model_validate(report).model_dump(mode='json')
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
    
    # mode='json' converts UUID to string automatically
    payload = [P2HReportListResponse.model_validate(r).model_dump(mode='json') for r in reports]
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
    
    payload = P2HReportResponse.model_validate(report).model_dump(mode='json')
    return base_response(message="Detail laporan P2H berhasil ditemukan", payload=payload)