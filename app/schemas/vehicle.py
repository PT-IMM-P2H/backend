from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from app.models.vehicle import VehicleType, ShiftType


# Vehicle Schemas
class VehicleBase(BaseModel):
    """Base vehicle schema"""
    no_lambung: str = Field(..., min_length=1, max_length=20)
    warna_no_lambung: Optional[str] = Field(None, max_length=20)
    plat_nomor: Optional[str] = Field(None, max_length=20)
    vehicle_type: VehicleType
    merk: Optional[str] = Field(None, max_length=50)
    stnk_expired: Optional[date] = None
    kir_expired: Optional[date] = None
    shift_type: ShiftType = Field(default=ShiftType.SHIFT)


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle"""
    no_lambung: Optional[str] = Field(None, min_length=1, max_length=20)
    warna_no_lambung: Optional[str] = Field(None, max_length=20)
    plat_nomor: Optional[str] = Field(None, max_length=20)
    vehicle_type: Optional[VehicleType] = None
    merk: Optional[str] = Field(None, max_length=50)
    stnk_expired: Optional[date] = None
    kir_expired: Optional[date] = None
    shift_type: Optional[ShiftType] = None
    is_active: Optional[bool] = None


class VehicleResponse(BaseModel):
    """Schema for vehicle response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    no_lambung: str
    warna_no_lambung: Optional[str]
    plat_nomor: Optional[str]
    vehicle_type: VehicleType
    merk: Optional[str]
    stnk_expired: Optional[date]
    kir_expired: Optional[date]
    is_active: bool
    shift_type: ShiftType
    created_at: datetime
    updated_at: datetime


class VehicleP2HStatus(BaseModel):
    """Schema for vehicle P2H status"""
    model_config = ConfigDict(from_attributes=True)
    
    vehicle: VehicleResponse
    can_submit_p2h: bool
    p2h_completed_today: bool
    current_shift: int
    shifts_completed: List[int]
    message: str
