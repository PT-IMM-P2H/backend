"""
P2H Repository - Database operations for P2H reports

Pure database queries - NO business logic
"""

from sqlalchemy.orm import Session, Query
from sqlalchemy import func, and_, extract
from typing import Optional, List
from datetime import date
from uuid import UUID

from app.models.p2h import P2HReport, P2HDetail, P2HDailyTracker
from .base import BaseRepository


class P2HRepository(BaseRepository[P2HReport]):
    """Repository for P2H Report database operations"""
    
    def __init__(self):
        super().__init__(P2HReport)
    
    def get_reports_query(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        vehicle_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> Query:
        """
        Get base query for P2H reports with optional filters.
        
        Args:
            db: Database session
            start_date: Filter by submission date >= start_date (already parsed)
            end_date: Filter by submission date <= end_date (already parsed)
            vehicle_id: Filter by vehicle ID
            status: Filter by overall status
            
        Returns:
            SQLAlchemy Query object
        """
        query = db.query(P2HReport)
        
        # Apply filters directly - no conditional checking
        if start_date is not None:
            query = query.filter(func.date(P2HReport.submission_date) >= start_date)
        
        if end_date is not None:
            query = query.filter(func.date(P2HReport.submission_date) <= end_date)
        
        if vehicle_id is not None:
            query = query.filter(P2HReport.vehicle_id == vehicle_id)
        
        if status is not None:
            query = query.filter(P2HReport.overall_status == status)
        
        return query
    
    def count_by_status(
        self,
        db: Session,
        status: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """
        Count P2H reports by status with optional date filters.
        
        Args:
            db: Database session
            status: Status to count ('normal', 'abnormal', 'warning')
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Count of reports
        """
        query = self.get_reports_query(db, start_date, end_date, status=status)
        return query.count() or 0
    
    def get_monthly_counts(
        self,
        db: Session,
        year: int,
        month: int,
        vehicle_type: Optional[str] = None
    ) -> dict:
        """
        Get P2H report counts by status for a specific month.
        
        Args:
            db: Database session
            year: Year to filter
            month: Month to filter (1-12)
            vehicle_type: Optional vehicle type filter
            
        Returns:
            Dict with counts: {"normal": int, "abnormal": int, "warning": int}
        """
        from app.models.vehicle import Vehicle
        
        # Base query with month/year filter
        query = db.query(P2HReport).filter(
            and_(
                extract('year', P2HReport.submission_date) == year,
                extract('month', P2HReport.submission_date) == month
            )
        )
        
        # Join with vehicle if vehicle_type filter is provided
        if vehicle_type is not None:
            query = query.join(Vehicle).filter(Vehicle.vehicle_type == vehicle_type)
        
        # Count by status
        normal = query.filter(P2HReport.overall_status == 'normal').count() or 0
        abnormal = query.filter(P2HReport.overall_status == 'abnormal').count() or 0
        warning = query.filter(P2HReport.overall_status == 'warning').count() or 0
        
        return {
            "normal": normal,
            "abnormal": abnormal,
            "warning": warning
        }
    
    def get_vehicles_reported_on_date(self, db: Session, report_date: date) -> int:
        """
        Count distinct vehicles that have reports on a specific date.
        
        Args:
            db: Database session
            report_date: Date to check
            
        Returns:
            Count of distinct vehicles
        """
        return db.query(func.count(func.distinct(P2HReport.vehicle_id))).filter(
            func.date(P2HReport.submission_date) == report_date
        ).scalar() or 0
    
    def get_daily_tracker(
        self,
        db: Session,
        vehicle_id: UUID,
        tracker_date: date
    ) -> Optional[P2HDailyTracker]:
        """
        Get daily tracker for a vehicle on a specific date.
        
        Args:
            db: Database session
            vehicle_id: Vehicle UUID
            tracker_date: Date to get tracker for
            
        Returns:
            P2HDailyTracker or None
        """
        return db.query(P2HDailyTracker).filter(
            and_(
                P2HDailyTracker.vehicle_id == vehicle_id,
                P2HDailyTracker.date == tracker_date
            )
        ).first()
    
    def create_daily_tracker(
        self,
        db: Session,
        vehicle_id: UUID,
        tracker_date: date
    ) -> P2HDailyTracker:
        """
        Create new daily tracker.
        
        Args:
            db: Database session
            vehicle_id: Vehicle UUID
            tracker_date: Date for tracker
            
        Returns:
            Created P2HDailyTracker
        """
        tracker = P2HDailyTracker(
            vehicle_id=vehicle_id,
            date=tracker_date,
            submission_count=0
        )
        return self.create(db, tracker)


# Singleton instance
p2h_repository = P2HRepository()
