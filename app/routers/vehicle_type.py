"""
Router for Vehicle Type endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.vehicle_type_repository import VehicleTypeRepository
from app.services.vehicle_type_service import VehicleTypeService
from app.schemas.vehicle_type import (
    VehicleTypeCreate,
    VehicleTypeUpdate,
    VehicleTypeResponse,
    VehicleTypeListResponse
)
from app.utils.response import base_response


router = APIRouter(prefix="/vehicle-types", tags=["vehicle-types"])


def get_vehicle_type_service(db: Session = Depends(get_db)) -> VehicleTypeService:
    """Dependency to get vehicle type service"""
    repository = VehicleTypeRepository(db)
    return VehicleTypeService(repository)


@router.get("/active", response_model=list[VehicleTypeResponse])
async def get_active_vehicle_types(
    service: VehicleTypeService = Depends(get_vehicle_type_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active vehicle types for dropdowns
    
    **Accessible by**: All authenticated users
    """
    vehicle_types = service.get_active_vehicle_types()
    return base_response(
        message="Tipe kendaraan aktif berhasil diambil",
        payload=vehicle_types,
        status_code=200
    )


@router.get("", response_model=VehicleTypeListResponse)
async def get_all_vehicle_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    service: VehicleTypeService = Depends(get_vehicle_type_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all vehicle types with pagination and filters
    
    **Accessible by**: Admin and Superadmin
    """
    result = service.get_all_vehicle_types(skip, limit, is_active, search)
    return base_response(
        message="Daftar tipe kendaraan berhasil diambil",
        payload=result,
        status_code=200
    )


@router.get("/{vehicle_type_id}", response_model=VehicleTypeResponse)
async def get_vehicle_type(
    vehicle_type_id: UUID,
    service: VehicleTypeService = Depends(get_vehicle_type_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get vehicle type by ID
    
    **Accessible by**: All authenticated users
    """
    vehicle_type = service.get_vehicle_type_by_id(vehicle_type_id)
    return base_response(
        message="Tipe kendaraan berhasil diambil",
        payload=vehicle_type,
        status_code=200
    )


@router.post("", response_model=VehicleTypeResponse, status_code=201)
async def create_vehicle_type(
    vehicle_type: VehicleTypeCreate,
    service: VehicleTypeService = Depends(get_vehicle_type_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create new vehicle type
    
    **Accessible by**: All authenticated users (page restricted to admin)
    **Requires**: name (unique)
    """
    created = service.create_vehicle_type(vehicle_type, current_user.id)
    return base_response(
        message="Tipe kendaraan berhasil dibuat",
        payload=created,
        status_code=201
    )


@router.put("/{vehicle_type_id}", response_model=VehicleTypeResponse)
async def update_vehicle_type(
    vehicle_type_id: UUID,
    vehicle_type: VehicleTypeUpdate,
    service: VehicleTypeService = Depends(get_vehicle_type_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update vehicle type
    
    **Accessible by**: All authenticated users (page restricted to admin)
    """
    updated = service.update_vehicle_type(vehicle_type_id, vehicle_type)
    return base_response(
        message="Tipe kendaraan berhasil diupdate",
        payload=updated,
        status_code=200
    )


@router.delete("/{vehicle_type_id}")
async def delete_vehicle_type(
    vehicle_type_id: UUID,
    service: VehicleTypeService = Depends(get_vehicle_type_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete vehicle type (soft delete)
    
    **Accessible by**: All authenticated users (page restricted to admin)
    """
    service.delete_vehicle_type(vehicle_type_id)
    return base_response(
        message="Tipe kendaraan berhasil dihapus",
        payload=None,
        status_code=200
    )
