"""
Dashboard Service - Business logic for dashboard operations

Orchestrates repositories and handles business logic
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, datetime

from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.p2h_repository import P2HRepository
from app.repositories.vehicle_repository import VehicleRepository


class DashboardService:
    """Service for dashboard business logic"""
    
    def __init__(self):
        self.dashboard_repo = DashboardRepository()
        self.p2h_repo = P2HRepository()
        self.vehicle_repo = VehicleRepository()
    
    def get_dashboard_statistics(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics with business logic.
        
        This method orchestrates multiple repository calls and applies
        business logic to calculate derived metrics.
        
        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with complete statistics
        """
        # Get base statistics from repository
        stats = self.dashboard_repo.get_statistics(db, start_date, end_date)
        
        # Business logic: Calculate pending P2H
        today = datetime.now().date()
        vehicles_reported_today = self.p2h_repo.get_vehicles_reported_on_date(db, today)
        total_pending_p2h = max(stats["total_vehicles"] - vehicles_reported_today, 0)
        
        # Add calculated field
        stats["total_pending_p2h"] = total_pending_p2h
        
        return stats
    
    def get_monthly_report_summary(
        self,
        db: Session,
        year: int,
        vehicle_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get monthly report summary with business logic.
        
        Args:
            db: Database session
            year: Year for the report
            vehicle_type: Optional vehicle type filter
            
        Returns:
            Dictionary with monthly data and summary
        """
        # Get monthly data from repository
        monthly_data = self.dashboard_repo.get_monthly_reports(db, year, vehicle_type)
        
        # Business logic: Calculate totals and percentages
        total_normal = sum(data[0] for data in monthly_data.values())
        total_abnormal = sum(data[1] for data in monthly_data.values())
        total_warning = sum(data[2] for data in monthly_data.values())
        total_reports = total_normal + total_abnormal + total_warning
        
        # Calculate percentages
        normal_percentage = (total_normal / total_reports * 100) if total_reports > 0 else 0
        abnormal_percentage = (total_abnormal / total_reports * 100) if total_reports > 0 else 0
        warning_percentage = (total_warning / total_reports * 100) if total_reports > 0 else 0
        
        return {
            "monthly_data": monthly_data,
            "summary": {
                "total_normal": total_normal,
                "total_abnormal": total_abnormal,
                "total_warning": total_warning,
                "total_reports": total_reports,
                "normal_percentage": round(normal_percentage, 2),
                "abnormal_percentage": round(abnormal_percentage, 2),
                "warning_percentage": round(warning_percentage, 2)
            }
        }
    
    def get_vehicle_type_breakdown(
        self,
        db: Session,
        vehicle_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get detailed breakdown for a specific vehicle type.
        
        Args:
            db: Database session
            vehicle_type: Vehicle type to analyze
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with vehicle type breakdown
        """
        # Get status counts for this vehicle type
        status_data = self.dashboard_repo.get_vehicle_type_status(
            db, vehicle_type, start_date, end_date
        )
        
        # Business logic: Calculate health score
        total = status_data["normal"] + status_data["abnormal"] + status_data["warning"]
        health_score = 0
        if total > 0:
            # Health score: Normal = 100%, Warning = 50%, Abnormal = 0%
            health_score = (
                (status_data["normal"] * 100 + status_data["warning"] * 50) / total
            )
        
        return {
            **status_data,
            "total_reports": total,
            "health_score": round(health_score, 2)
        }


# Singleton instance
dashboard_service = DashboardService()
