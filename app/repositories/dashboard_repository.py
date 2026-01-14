"""
Dashboard Repository - Database operations for dashboard statistics

Pure database queries - NO business logic
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import Optional, Dict, Any
from datetime import date
from uuid import UUID

from app.models.p2h import P2HReport
from app.models.vehicle import Vehicle
from .p2h_repository import P2HRepository


class DashboardRepository:
    """Repository for dashboard-related database operations"""
    
    def __init__(self):
        self.p2h_repo = P2HRepository()
    
    def get_statistics(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Get dashboard statistics with optional date filters.
        
        Args:
            db: Database session
            start_date: Start date for filtering (already parsed date object)
            end_date: End date for filtering (already parsed date object)
            
        Returns:
            Dictionary with statistics
        """
        # Total vehicles (not affected by date filter)
        total_vehicles = db.query(func.count(Vehicle.id)).scalar() or 0
        
        # P2H counts by status with date filter
        total_normal = self.p2h_repo.count_by_status(db, 'normal', start_date, end_date)
        total_abnormal = self.p2h_repo.count_by_status(db, 'abnormal', start_date, end_date)
        total_warning = self.p2h_repo.count_by_status(db, 'warning', start_date, end_date)
        
        # Total completed P2H
        total_completed = self.p2h_repo.get_reports_query(
            db, start_date, end_date
        ).count() or 0
        
        return {
            "total_vehicles": total_vehicles,
            "total_normal": total_normal,
            "total_abnormal": total_abnormal,
            "total_warning": total_warning,
            "total_completed_p2h": total_completed,
        }
    
    def get_monthly_reports(
        self,
        db: Session,
        year: int,
        vehicle_type: Optional[str] = None
    ) -> Dict[str, list]:
        """
        Get monthly P2H report counts for the entire year.
        
        Args:
            db: Database session
            year: Year to get reports for
            vehicle_type: Optional vehicle type filter
            
        Returns:
            Dictionary with monthly data {month_name: [normal, abnormal, warning]}
        """
        month_names = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        
        monthly_data = {}
        
        for month_num in range(1, 13):
            counts = self.p2h_repo.get_monthly_counts(
                db, year, month_num, vehicle_type
            )
            month_name = month_names[month_num - 1]
            monthly_data[month_name] = [
                counts["normal"],
                counts["abnormal"],
                counts["warning"]
            ]
        
        return monthly_data
    
    def get_vehicle_type_status(
        self,
        db: Session,
        vehicle_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Get P2H status counts for a specific vehicle type.
        
        Args:
            db: Database session
            vehicle_type: Vehicle type to filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with counts by status
        """
        # Base query with vehicle type join
        query = db.query(P2HReport).join(Vehicle).filter(
            Vehicle.vehicle_type == vehicle_type
        )
        
        # Apply date filters
        if start_date is not None:
            query = query.filter(func.date(P2HReport.submission_date) >= start_date)
        
        if end_date is not None:
            query = query.filter(func.date(P2HReport.submission_date) <= end_date)
        
        # Count by status
        normal = query.filter(P2HReport.overall_status == 'normal').count() or 0
        abnormal = query.filter(P2HReport.overall_status == 'abnormal').count() or 0
        warning = query.filter(P2HReport.overall_status == 'warning').count() or 0
        
        return {
            "normal": normal,
            "abnormal": abnormal,
            "warning": warning
        }
    
    def get_vehicle_types(self, db: Session) -> list:
        """
        Get all distinct vehicle types from database.
        
        Args:
            db: Database session
            
        Returns:
            List of vehicle type strings
        """
        result = db.query(Vehicle.vehicle_type).distinct().all()
        return [row[0] for row in result if row[0]]


# Singleton instance
dashboard_repository = DashboardRepository()
