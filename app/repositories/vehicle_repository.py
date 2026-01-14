"""
Vehicle Repository - Database operations for vehicles

Pure database queries - NO business logic
"""

from sqlalchemy.orm import Session, Query
from typing import Optional, List
from uuid import UUID

from app.models.vehicle import Vehicle
from .base import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    """Repository for Vehicle database operations"""
    
    def __init__(self):
        super().__init__(Vehicle)
    
    def get_vehicles_query(
        self,
        db: Session,
        vehicle_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Query:
        """
        Get base query for vehicles with optional filters.
        
        Args:
            db: Database session
            vehicle_type: Filter by vehicle type
            is_active: Filter by active status
            
        Returns:
            SQLAlchemy Query object
        """
        query = db.query(Vehicle)
        
        # Apply filters directly - no conditional checking
        if vehicle_type is not None:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)
        
        if is_active is not None:
            query = query.filter(Vehicle.is_active == is_active)
        
        return query
    
    def count_total(self, db: Session) -> int:
        """
        Count total vehicles.
        
        Args:
            db: Database session
            
        Returns:
            Total count
        """
        return db.query(Vehicle).count() or 0
    
    def get_by_license_plate(self, db: Session, license_plate: str) -> Optional[Vehicle]:
        """
        Get vehicle by license plate.
        
        Args:
            db: Database session
            license_plate: License plate number
            
        Returns:
            Vehicle or None
        """
        return db.query(Vehicle).filter(
            Vehicle.license_plate == license_plate
        ).first()
    
    def get_active_vehicles(self, db: Session) -> List[Vehicle]:
        """
        Get all active vehicles.
        
        Args:
            db: Database session
            
        Returns:
            List of active vehicles
        """
        return self.get_vehicles_query(db, is_active=True).all()


# Singleton instance
vehicle_repository = VehicleRepository()
