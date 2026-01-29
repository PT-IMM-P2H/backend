from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_role
from app.utils.response import base_response
from app.utils.datetime import get_current_datetime
from app.services.dashboard_service import dashboard_service
from app.repositories.dashboard_repository import dashboard_repository

router = APIRouter(
    prefix="/dashboard", 
    tags=["Dashboard"],
    dependencies=[Depends(require_role([UserRole.admin, UserRole.superadmin]))]
)


@router.get("/statistics")
async def get_dashboard_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics including total vehicles, P2H reports by status, etc.
    Optional filtering with start_date, end_date (format: YYYY-MM-DD), and vehicle_type.
    
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
    stats = dashboard_service.get_dashboard_statistics(db, start_dt, end_dt, vehicle_type)
    
    # Controller layer: Format response
    return base_response(
        message="Statistik dashboard berhasil diambil",
        payload={
            **stats,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_type": vehicle_type
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
        year = get_current_datetime().year
    
    current_year = get_current_datetime().year
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


@router.get("/card-details/{card_type}")
async def get_card_details(
    card_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed list for each dashboard card type.
    
    Card types:
    - total_vehicles: All registered vehicles
    - total_normal: Vehicles with normal status
    - total_abnormal: Vehicles with abnormal status
    - total_warning: Vehicles with warning status
    - total_completed: Vehicles that have completed P2H
    - total_pending: Vehicles pending P2H
    """
    from app.models.p2h import P2HReport
    from app.models.vehicle import Vehicle
    from sqlalchemy import func, distinct
    
    # Parse dates if provided
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")
    
    result_list = []
    
    if card_type == "total_vehicles":
        # Get all vehicles
        vehicles = db.query(Vehicle).limit(limit).all()
        result_list = [
            {
                "no_lambung": v.no_lambung,
                "plat_nomor": v.plat_nomor,
                "vehicle_type": v.vehicle_type.value if hasattr(v.vehicle_type, 'value') else str(v.vehicle_type) if v.vehicle_type else None,
                "merk": v.merk,
                "status": "registered"
            }
            for v in vehicles
        ]
        
    elif card_type in ["total_normal", "total_abnormal", "total_warning"]:
        # Get reports by status
        status_map = {
            "total_normal": "normal",
            "total_abnormal": "abnormal",
            "total_warning": "warning"
        }
        status = status_map[card_type]
        
        query = db.query(P2HReport).join(Vehicle).filter(
            P2HReport.overall_status == status
        )
        
        if start_dt:
            query = query.filter(func.date(P2HReport.submission_date) >= start_dt)
        if end_dt:
            query = query.filter(func.date(P2HReport.submission_date) <= end_dt)
        
        reports = query.order_by(P2HReport.submission_date.desc()).limit(limit).all()
        
        result_list = [
            {
                "no_lambung": r.vehicle.no_lambung if r.vehicle else None,
                "plat_nomor": r.vehicle.plat_nomor if r.vehicle else None,
                "vehicle_type": r.vehicle.vehicle_type.value if (r.vehicle and hasattr(r.vehicle.vehicle_type, 'value')) else str(r.vehicle.vehicle_type) if (r.vehicle and r.vehicle.vehicle_type) else None,
                "merk": r.vehicle.merk if r.vehicle else None,
                "status": r.overall_status,
                "submission_date": r.submission_date.isoformat() if r.submission_date else None,
                "operator": r.user.full_name if r.user else None
            }
            for r in reports
        ]
        
    elif card_type == "total_completed":
        # Get vehicles that completed P2H
        query = db.query(P2HReport).join(Vehicle)
        
        if start_dt:
            query = query.filter(func.date(P2HReport.submission_date) >= start_dt)
        if end_dt:
            query = query.filter(func.date(P2HReport.submission_date) <= end_dt)
        
        reports = query.order_by(P2HReport.submission_date.desc()).limit(limit).all()
        
        result_list = [
            {
                "no_lambung": r.vehicle.no_lambung if r.vehicle else None,
                "plat_nomor": r.vehicle.plat_nomor if r.vehicle else None,
                "vehicle_type": r.vehicle.vehicle_type.value if (r.vehicle and hasattr(r.vehicle.vehicle_type, 'value')) else str(r.vehicle.vehicle_type) if (r.vehicle and r.vehicle.vehicle_type) else None,
                "merk": r.vehicle.merk if r.vehicle else None,
                "status": r.overall_status,
                "submission_date": r.submission_date.isoformat() if r.submission_date else None,
                "operator": r.user.full_name if r.user else None
            }
            for r in reports
        ]
        
    elif card_type == "total_pending":
        # Get vehicles without P2H today (or in date range)
        today = get_current_datetime().date()
        check_date = end_dt if end_dt else today
        
        # Get vehicles that have NOT submitted P2H on check_date
        subquery = db.query(distinct(P2HReport.vehicle_id)).filter(
            func.date(P2HReport.submission_date) == check_date
        ).subquery()
        
        vehicles = db.query(Vehicle).filter(
            ~Vehicle.id.in_(subquery)
        ).limit(limit).all()
        
        result_list = [
            {
                "no_lambung": v.no_lambung,
                "plat_nomor": v.plat_nomor,
                "vehicle_type": v.vehicle_type.value if hasattr(v.vehicle_type, 'value') else str(v.vehicle_type) if v.vehicle_type else None,
                "merk": v.merk,
                "status": "pending"
            }
            for v in vehicles
        ]
    
    else:
        raise HTTPException(status_code=400, detail=f"Invalid card_type: {card_type}")
    
    return base_response(
        message=f"Detail untuk {card_type} berhasil diambil",
        payload={
            "card_type": card_type,
            "count": len(result_list),
            "items": result_list
        }
    )
