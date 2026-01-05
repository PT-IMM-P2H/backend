from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.vehicle import VehicleType
from app.models.checklist import ChecklistTemplate
from app.schemas.p2h import (
    ChecklistItemResponse,
    P2HReportSubmit,
    P2HReportResponse,
    P2HReportListResponse
)
from app.services.p2h_service import p2h_service
from app.dependencies import get_current_user
from app.utils.response import base_response  # Import wrapper response standar

router = APIRouter()


@router.get("/checklist/{vehicle_type}")
async def get_checklist(
    vehicle_type: VehicleType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get checklist items for a specific vehicle type.
    """
    checklist_items = db.query(ChecklistTemplate).filter(
        ChecklistTemplate.vehicle_type == vehicle_type,
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
    """
    Check P2H status for a vehicle.
    """
    try:
        p2h_status = p2h_service.get_vehicle_p2h_status(db, vehicle_id)
        return base_response(
            message="Status P2H kendaraan berhasil diperiksa",
            payload=p2h_status
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_p2h(
    submission: P2HReportSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a P2H report with standardized response and notification integration.
    """
    try:
        report = await p2h_service.submit_p2h(db, current_user, submission)
        
        # Load relationships for response
        db.refresh(report)
        
        payload = P2HReportResponse.model_validate(report).model_dump()
        
        return base_response(
            message="Laporan P2H berhasil disubmit",
            payload=payload,
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/reports")
async def get_p2h_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of P2H reports with pagination.
    """
    from app.models.p2h import P2HReport
    
    reports = db.query(P2HReport).order_by(
        P2HReport.submission_date.desc(),
        P2HReport.submission_time.desc()
    ).offset(skip).limit(limit).all()
    
    payload = [P2HReportListResponse.model_validate(r).model_dump() for r in reports]
    
    return base_response(
        message="Daftar laporan P2H berhasil diambil",
        payload=payload
    )


@router.get("/reports/{report_id}")
async def get_p2h_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed P2H report by ID.
    """
    from app.models.p2h import P2HReport
    
    report = db.query(P2HReport).filter(P2HReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laporan P2H tidak ditemukan"
        )
    
    payload = P2HReportResponse.model_validate(report).model_dump()
    
    return base_response(
        message="Detail laporan P2H berhasil ditemukan",
        payload=payload
    )