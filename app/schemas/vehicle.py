from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from app.models.vehicle import VehicleType, ShiftType


# Nested schemas for relations
class UserSimpleResponse(BaseModel):
    """Simple user info for vehicle response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    full_name: str
    phone_number: Optional[str]
    email: Optional[str]


class CompanySimpleResponse(BaseModel):
    """Simple company info for vehicle response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    nama_perusahaan: str


# Vehicle Schemas
class VehicleBase(BaseModel):
    """Base vehicle schema"""
    no_lambung: str = Field(..., min_length=1, max_length=20)
    warna_no_lambung: Optional[str] = Field(None, max_length=20)
    plat_nomor: Optional[str] = Field(None, max_length=20)
    vehicle_type: VehicleType
    merk: Optional[str] = Field(None, max_length=50)
    user_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    no_rangka: Optional[str] = Field(None, max_length=100)
    no_mesin: Optional[str] = Field(None, max_length=100)
    stnk_expiry: Optional[date] = None
    pajak_expiry: Optional[date] = None
    kir_expiry: Optional[date] = None
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
    user_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    no_rangka: Optional[str] = Field(None, max_length=100)
    no_mesin: Optional[str] = Field(None, max_length=100)
    stnk_expiry: Optional[date] = None
    pajak_expiry: Optional[date] = None
    kir_expiry: Optional[date] = None
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
    user_id: Optional[UUID]
    company_id: Optional[UUID]
    no_rangka: Optional[str]
    no_mesin: Optional[str]
    stnk_expiry: Optional[date]
    pajak_expiry: Optional[date]
    kir_expiry: Optional[date]
    is_active: bool
    shift_type: ShiftType
    created_at: datetime
    updated_at: datetime
    
    # Nested relations
    user: Optional[UserSimpleResponse] = None
    company: Optional[CompanySimpleResponse] = None


class VehicleP2HStatus(BaseModel):
    """Schema for vehicle P2H status"""
    model_config = ConfigDict(from_attributes=True)
    
    vehicle: VehicleResponse
    can_submit_p2h: bool
    p2h_completed_today: bool
    current_shift: int
    shifts_completed: List[int]
    message: str
