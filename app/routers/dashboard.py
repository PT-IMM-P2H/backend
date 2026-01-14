from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import calendar

from app.database import get_db
from app.models.p2h import P2HReport
from app.models.vehicle import Vehicle
from app.models.user import User
from app.dependencies import get_current_user
from app.utils.response import base_response

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
    """
    
    # Total vehicles (tidak terpengaruh filter tanggal)
    total_vehicles = db.query(func.count(Vehicle.id)).scalar()
    
    # Build base query untuk P2H reports
    base_query = db.query(P2HReport)
    
    # Apply date filters if provided
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date).date()
            base_query = base_query.filter(func.date(P2HReport.submission_date) >= start_dt)
        except ValueError:
            pass  # Ignore invalid date format
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date).date()
            base_query = base_query.filter(func.date(P2HReport.submission_date) <= end_dt)
        except ValueError:
            pass  # Ignore invalid date format
    
    # P2H Report statistics by status
    total_normal = base_query.filter(P2HReport.overall_status == 'normal').count() or 0
    total_abnormal = base_query.filter(P2HReport.overall_status == 'abnormal').count() or 0
    total_warning = base_query.filter(P2HReport.overall_status == 'warning').count() or 0
    
    # Total P2H reports
    total_completed_p2h = base_query.count() or 0
    
    # Pending P2H (kendaraan yang belum ada laporan hari ini)
    today = datetime.now().date()
    vehicles_reported_today = db.query(func.count(func.distinct(P2HReport.vehicle_id))).filter(
        func.date(P2HReport.submission_date) == today
    ).scalar() or 0
    
    total_pending_p2h = total_vehicles - vehicles_reported_today
    
    return base_response(
        message="Statistik dashboard berhasil diambil",
        payload={
            "total_vehicles": total_vehicles or 0,
            "total_normal": total_normal,
            "total_abnormal": total_abnormal,
            "total_warning": total_warning,
            "total_completed_p2h": total_completed_p2h,
            "total_pending_p2h": max(total_pending_p2h, 0),
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
    """
    
    # Default to current year if not specified
    if year is None:
        year = datetime.now().year
    
    # Initialize monthly data structure
    monthly_data = {}
    
    # Get Indonesian month names
    month_names = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    
    for month_num in range(1, 13):
        month_name = month_names[month_num - 1]
        
        # Base query
        base_query = db.query(P2HReport).filter(
            extract('year', P2HReport.submission_date) == year,
            extract('month', P2HReport.submission_date) == month_num
        )
        
        # Apply vehicle type filter if specified
        if vehicle_type and vehicle_type != "":
            base_query = base_query.join(Vehicle).filter(
                Vehicle.vehicle_type == vehicle_type
            )
        
        # Count by status
        normal_count = base_query.filter(P2HReport.overall_status == 'normal').count()
        abnormal_count = base_query.filter(P2HReport.overall_status == 'abnormal').count()
        warning_count = base_query.filter(P2HReport.overall_status == 'warning').count()
        
        monthly_data[month_name] = [normal_count, abnormal_count, warning_count]
    
    return base_response(
        message="Data bulanan berhasil diambil",
        payload={
            "year": year,
            "vehicle_type": vehicle_type or "all",
            "monthly_data": monthly_data
        }
    )


@router.get("/vehicle-types")
async def get_vehicle_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of unique vehicle types from vehicles table.
    """
    
    vehicle_types = db.query(Vehicle.vehicle_type).distinct().all()
    
    # Extract values from tuples and convert enum to string
    vehicle_type_list = [vt[0].value if hasattr(vt[0], 'value') else str(vt[0]) for vt in vehicle_types if vt[0]]
    
    return base_response(
        message="Tipe kendaraan berhasil diambil",
        payload={
            "vehicle_types": sorted(vehicle_type_list)
        }
    )


@router.get("/vehicle-type-status")
async def get_vehicle_type_status(
    vehicle_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get P2H status statistics (normal, abnormal, warning) for a specific vehicle type.
    """
    
    if not vehicle_type:
        raise HTTPException(status_code=400, detail="vehicle_type parameter is required")
    
    # Base query for the specific vehicle type
    base_query = db.query(P2HReport).join(Vehicle).filter(
        Vehicle.vehicle_type == vehicle_type
    )
    
    # Count by status
    normal_count = base_query.filter(P2HReport.overall_status == 'normal').count()
    abnormal_count = base_query.filter(P2HReport.overall_status == 'abnormal').count()
    warning_count = base_query.filter(P2HReport.overall_status == 'warning').count()
    
    return base_response(
        message=f"Status untuk tipe kendaraan {vehicle_type} berhasil diambil",
        payload={
            "vehicle_type": vehicle_type,
            "normal": normal_count,
            "abnormal": abnormal_count,
            "warning": warning_count,
            "total": normal_count + abnormal_count + warning_count
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
    
    reports = db.query(P2HReport).order_by(
        P2HReport.submission_date.desc(),
        P2HReport.submission_time.desc()
    ).limit(limit).all()
    
    return {
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
