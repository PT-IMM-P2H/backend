from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.utils.response import base_response
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/statistics")
async def get_dashboard_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics including total vehicles, P2H reports by status, etc.
    Optional date filtering with start_date and end_date (format: YYYY-MM-DD).
    
    IMPROVED: Following 3-Layer Architecture
    - Controller: HTTP logic, validation, response formatting
    - Service: Business logic, orchestration, calculations
    - Repository: Pure database operations
    """
    
    # Controller layer: Parse & validate input
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid start_date format: {start_date}. Expected YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date).date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid end_date format: {end_date}. Expected YYYY-MM-DD"
            )
    
    # Service layer: Business logic & orchestration
    stats = dashboard_service.get_dashboard_statistics(db, start_dt, end_dt)
    
    # Controller layer: Format response
    return base_response(
        message="Statistik dashboard berhasil diambil",
        payload={
            **stats,
            "filters": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    )


@router.get("/monthly-reports")
async def get_monthly_reports(
    year: Optional[int] = None,
    vehicle_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly P2H reports grouped by status (normal, abnormal, warning).
    Returns data for each month in the specified year.
    
    IMPROVED: Following 3-Layer Architecture
    - Controller: Validation & response formatting
    - Service: Business logic (default year, calculations)
    - Repository: Database queries
    """
    
    # Controller layer: Validation
    if year is None:
        year = datetime.now().year
    
    current_year = datetime.now().year
    if year < 2020 or year > current_year + 5:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid year: {year}. Must be between 2020 and {current_year + 5}"
        )
    
    # Service layer: Business logic & orchestration
    result = dashboard_service.get_monthly_report_summary(db, year, vehicle_type)
    
    # Controller layer: Format response
    return base_response(
        message="Data bulanan berhasil diambil",
        payload={
            "year": year,
            "vehicle_type": vehicle_type or "all",
            **result
        }
    )


@router.get("/vehicle-types")
async def get_vehicle_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of unique vehicle types from vehicles table.
    
    IMPROVED: Using repository pattern
    """
    
    # Get data from repository
    vehicle_types = dashboard_repository.get_vehicle_types(db)
    
    # Business logic: extract enum values and sort
    vehicle_type_list = [
        vt.value if hasattr(vt, 'value') else str(vt) 
        for vt in vehicle_types
    ]
    
    return base_response(
        message="Tipe kendaraan berhasil diambil",
        payload={
            "vehicle_types": sorted(vehicle_type_list)
        }
    )


@router.get("/vehicle-type-status")
async def get_vehicle_type_status(
    vehicle_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get P2H status statistics (normal, abnormal, warning) for a specific vehicle type.
    
    IMPROVED: Following Repository Pattern
    - Controller validates required parameters
    - Repository receives clean, typed parameters
    """
    
    # Validate required parameter
    if not vehicle_type:
        raise HTTPException(
            status_code=400,
            detail="vehicle_type parameter is required"
        )
    
    # Parse & validate date parameters
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid start_date format: {start_date}"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date).date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid end_date format: {end_date}"
            )
    
    # Get data from repository with clean parameters
    status_counts = dashboard_repository.get_vehicle_type_status(
        db, vehicle_type, start_dt, end_dt
    )
    
    # Calculate total (business logic)
    total = sum(status_counts.values())
    
    return base_response(
        message=f"Status untuk tipe kendaraan {vehicle_type} berhasil diambil",
        payload={
            "vehicle_type": vehicle_type,
            **status_counts,
            "total": total
        }
    )


@router.get("/recent-reports")
async def get_recent_reports(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent P2H reports with vehicle and user information.
    """
    
    from app.models.p2h import P2HReport
    
    reports = db.query(P2HReport).order_by(
        P2HReport.submission_date.desc(),
        P2HReport.submission_time.desc()
    ).limit(limit).all()
    
    report_data = {
        "reports": [
            {
                "id": str(report.id),
                "submission_date": report.submission_date.isoformat() if report.submission_date else None,
                "submission_time": report.submission_time.isoformat() if report.submission_time else None,
                "overall_status": report.overall_status,
                "vehicle": {
                    "no_lambung": report.vehicle.no_lambung,
                    "plat_nomor": report.vehicle.plat_nomor,
                    "vehicle_type": report.vehicle.vehicle_type,
                    "merk": report.vehicle.merk
                } if report.vehicle else None,
                "user": {
                    "full_name": report.user.full_name,
                    "email": report.user.email
                } if report.user else None
            }
            for report in reports
        ]
    }
    
    return base_response(
        message="Laporan terbaru berhasil diambil",
        payload=report_data
    )
