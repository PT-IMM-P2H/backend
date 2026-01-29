"""
Vehicle Repository - Database operations for vehicles

Pure database queries - NO business logic
"""

from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID

from app.models.vehicle import Vehicle
from app.utils.vehicle_utils import normalize_hull_number
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
    
    def get_by_hull_number(self, db: Session, hull_number: str) -> Optional[Vehicle]:
        """
        Get vehicle by hull number (normalized search).
        Mencari dengan normalisasi - mengabaikan spasi, titik, case, dll.
        
        Args:
            db: Database session
            hull_number: Hull number dalam format apapun (P309, P.309, p 309, dll)
            
        Returns:
            Vehicle or None
        """
        # Normalize input untuk comparison
        normalized_input = normalize_hull_number(hull_number)
        
        # Get all vehicles dan cari yang match setelah normalisasi
        # Ini cara simple - untuk performa lebih baik bisa pakai SQL function
        vehicles = db.query(Vehicle).filter(Vehicle.no_lambung.isnot(None)).all()
        
        for vehicle in vehicles:
            if normalize_hull_number(vehicle.no_lambung) == normalized_input:
                return vehicle
        
        return None
    
    def search_vehicles(
        self,
        db: Session,
        search_query: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Vehicle]:
        """
        Search vehicles dengan normalized hull number search.
        
        Args:
            db: Database session
            search_query: Query untuk search (nomor lambung, plat nomor, dll)
            vehicle_type: Filter by vehicle type
            is_active: Filter by active status
            
        Returns:
            List of matching vehicles
        """
        query = self.get_vehicles_query(db, vehicle_type, is_active)
        
        if search_query and search_query.strip():
            # Normalize search query
            normalized_query = normalize_hull_number(search_query)
            
            # Search di multiple fields
            # Untuk hull number, kita perlu normalize di database juga
            # Menggunakan SQL REPLACE untuk hapus karakter khusus
            query = query.filter(
                (func.upper(func.replace(func.replace(func.replace(
                    Vehicle.no_lambung, '.', ''), ' ', ''), ',', '')).like(f"%{normalized_query}%")) |
                (func.upper(Vehicle.plat_nomor).like(f"%{search_query.upper()}%")) |
                (func.upper(Vehicle.merk).like(f"%{search_query.upper()}%"))
            )
        
        return query.all()


# Singleton instance
vehicle_repository = VehicleRepository()
