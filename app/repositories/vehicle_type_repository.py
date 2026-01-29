"""
Repository for Vehicle Type operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.vehicle_type import VehicleTypeModel
from app.schemas.vehicle_type import VehicleTypeCreate, VehicleTypeUpdate


class VehicleTypeRepository:
    """Repository for Vehicle Type CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[VehicleTypeModel]:
        """Get all vehicle types with optional filters"""
        query = self.db.query(VehicleTypeModel).filter(VehicleTypeModel.is_deleted == False)
        
        if is_active is not None:
            query = query.filter(VehicleTypeModel.is_active == is_active)
        
        if search:
            query = query.filter(
                or_(
                    VehicleTypeModel.name.ilike(f"%{search}%"),
                    VehicleTypeModel.description.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(VehicleTypeModel.name).offset(skip).limit(limit).all()
    
    def count(
        self, 
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """Count vehicle types with filters"""
        query = self.db.query(VehicleTypeModel).filter(VehicleTypeModel.is_deleted == False)
        
        if is_active is not None:
            query = query.filter(VehicleTypeModel.is_active == is_active)
        
        if search:
            query = query.filter(
                or_(
                    VehicleTypeModel.name.ilike(f"%{search}%"),
                    VehicleTypeModel.description.ilike(f"%{search}%")
                )
            )
        
        return query.count()
    
    def get_by_id(self, vehicle_type_id: UUID) -> Optional[VehicleTypeModel]:
        """Get vehicle type by ID"""
        return self.db.query(VehicleTypeModel).filter(
            VehicleTypeModel.id == vehicle_type_id,
            VehicleTypeModel.is_deleted == False
        ).first()
    
    def get_by_name(self, name: str) -> Optional[VehicleTypeModel]:
        """Get vehicle type by name"""
        return self.db.query(VehicleTypeModel).filter(
            VehicleTypeModel.name == name,
            VehicleTypeModel.is_deleted == False
        ).first()
    
    def create(self, vehicle_type: VehicleTypeCreate, created_by: Optional[UUID] = None) -> VehicleTypeModel:
        """Create new vehicle type"""
        db_vehicle_type = VehicleTypeModel(
            **vehicle_type.dict(),
            created_by=created_by
        )
        self.db.add(db_vehicle_type)
        self.db.commit()
        self.db.refresh(db_vehicle_type)
        return db_vehicle_type
    
    def update(self, vehicle_type_id: UUID, vehicle_type: VehicleTypeUpdate) -> Optional[VehicleTypeModel]:
        """Update vehicle type"""
        db_vehicle_type = self.get_by_id(vehicle_type_id)
        if not db_vehicle_type:
            return None
        
        update_data = vehicle_type.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle_type, field, value)
        
        db_vehicle_type.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_vehicle_type)
        return db_vehicle_type
    
    def delete(self, vehicle_type_id: UUID) -> bool:
        """Soft delete vehicle type"""
        db_vehicle_type = self.get_by_id(vehicle_type_id)
        if not db_vehicle_type:
            return False
        
        db_vehicle_type.is_deleted = True
        db_vehicle_type.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_active(self) -> List[VehicleTypeModel]:
        """Get only active vehicle types"""
        return self.get_all(is_active=True, limit=1000)
