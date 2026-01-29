"""
Schemas for Vehicle Type management
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class VehicleTypeBase(BaseModel):
    """Base schema for Vehicle Type"""
    name: str = Field(..., min_length=1, max_length=100, description="Nama tipe kendaraan")
    description: Optional[str] = Field(None, description="Deskripsi tipe kendaraan")


class VehicleTypeCreate(VehicleTypeBase):
    """Schema for creating vehicle type"""
    is_active: bool = Field(default=True, description="Status aktif")


class VehicleTypeUpdate(BaseModel):
    """Schema for updating vehicle type"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleTypeResponse(VehicleTypeBase):
    """Schema for vehicle type response"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class VehicleTypeListResponse(BaseModel):
    """Schema for list of vehicle types"""
    total: int
    items: list[VehicleTypeResponse]
