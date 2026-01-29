"""
Service for Vehicle Type business logic
"""
from typing import List, Optional
from uuid import UUID

from app.repositories.vehicle_type_repository import VehicleTypeRepository
from app.schemas.vehicle_type import VehicleTypeCreate, VehicleTypeUpdate, VehicleTypeResponse
from app.exceptions import ConflictException, NotFoundException


class VehicleTypeService:
    """Service for Vehicle Type operations"""
    
    def __init__(self, repository: VehicleTypeRepository):
        self.repository = repository
    
    def get_all_vehicle_types(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> dict:
        """Get all vehicle types with pagination"""
        vehicle_types = self.repository.get_all(skip, limit, is_active, search)
        total = self.repository.count(is_active, search)
        
        # Convert SQLAlchemy models to Pydantic schemas
        items = [VehicleTypeResponse.model_validate(vt) for vt in vehicle_types]
        
        return {
            "total": total,
            "items": [item.model_dump(mode='json') for item in items]
        }
    
    def get_active_vehicle_types(self) -> List[dict]:
        """Get only active vehicle types for dropdowns"""
        vehicle_types = self.repository.get_active()
        # Convert to Pydantic schemas then to dict
        return [VehicleTypeResponse.model_validate(vt).model_dump(mode='json') for vt in vehicle_types]
    
    def get_vehicle_type_by_id(self, vehicle_type_id: UUID) -> dict:
        """Get vehicle type by ID"""
        vehicle_type = self.repository.get_by_id(vehicle_type_id)
        if not vehicle_type:
            raise NotFoundException("Tipe kendaraan tidak ditemukan")
        return VehicleTypeResponse.model_validate(vehicle_type).model_dump(mode='json')
    
    def create_vehicle_type(
        self, 
        vehicle_type: VehicleTypeCreate,
        created_by: Optional[UUID] = None
    ) -> dict:
        """Create new vehicle type"""
        # Check duplicate name
        existing = self.repository.get_by_name(vehicle_type.name)
        if existing:
            raise ConflictException(f"Tipe kendaraan '{vehicle_type.name}' sudah ada")
        
        created = self.repository.create(vehicle_type, created_by)
        return VehicleTypeResponse.model_validate(created).model_dump(mode='json')
    
    def update_vehicle_type(
        self,
        vehicle_type_id: UUID,
        vehicle_type: VehicleTypeUpdate
    ) -> dict:
        """Update vehicle type"""
        # Check if exists
        existing = self.repository.get_by_id(vehicle_type_id)
        if not existing:
            raise NotFoundException("Tipe kendaraan tidak ditemukan")
        
        # Check duplicate name if name is being updated
        if vehicle_type.name and vehicle_type.name != existing.name:
            duplicate = self.repository.get_by_name(vehicle_type.name)
            if duplicate:
                raise ConflictException(f"Tipe kendaraan '{vehicle_type.name}' sudah ada")
        
        updated = self.repository.update(vehicle_type_id, vehicle_type)
        if not updated:
            raise NotFoundException("Tipe kendaraan tidak ditemukan")
        
        return VehicleTypeResponse.model_validate(updated).model_dump(mode='json')
    
    def delete_vehicle_type(self, vehicle_type_id: UUID) -> bool:
        """Delete vehicle type (soft delete)"""
        success = self.repository.delete(vehicle_type_id)
        if not success:
            raise NotFoundException("Tipe kendaraan tidak ditemukan")
        return True
