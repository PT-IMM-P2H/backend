from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, time, datetime
from typing import Optional, List
from uuid import UUID

from app.models.p2h import InspectionStatus
from app.models.vehicle import VehicleType


# --- Checklist Schemas ---

class ChecklistItemCreate(BaseModel):
    """Schema baru untuk menambah pertanyaan dari Front-End (Modal Tambah Pertanyaan)"""
    question_text: str = Field(..., min_length=3, description="Isi teks pertanyaan")
    section_name: str = Field(..., description="Kategori pertanyaan (e.g., REM, RODA)")
    vehicle_tags: List[str] = Field(..., description="Daftar tipe kendaraan (e.g., ['LV', 'Bus'])")
    applicable_shifts: List[str] = Field(..., description="Shift berlakunya pertanyaan")
    options: List[str] = Field(default=["Baik", "Abnormal"], description="Pilihan jawaban")
    item_order: int = Field(..., ge=1)

class ChecklistItemResponse(BaseModel):
    """Schema for checklist item response - Diperbarui untuk mendukung Tagging"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    # Tetap pertahankan field lama agar tidak error, tapi tambahkan field baru
    vehicle_type: Optional[VehicleType] = None 
    vehicle_tags: List[str] = []
    applicable_shifts: List[str] = []
    options: List[str] = []
    section_name: str
    item_name: str # Mapping dari question_text di DB
    item_order: int


# --- P2H Detail Schemas ---

class P2HDetailSubmit(BaseModel):
    """Schema for submitting P2H detail"""
    checklist_item_id: UUID
    status: InspectionStatus
    keterangan: Optional[str] = None
    
    @field_validator('keterangan')
    @classmethod
    def validate_keterangan(cls, v, info):
        """Validate that keterangan is required for abnormal/warning status"""
        status = info.data.get('status')
        if status in [InspectionStatus.ABNORMAL, InspectionStatus.WARNING]:
            if not v or v.strip() == '':
                raise ValueError('Keterangan wajib diisi untuk status Abnormal atau Warning')
        return v


class P2HDetailResponse(BaseModel):
    """Schema for P2H detail response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    checklist_item: ChecklistItemResponse
    status: InspectionStatus
    keterangan: Optional[str]


# --- P2H Report Schemas ---

class P2HReportSubmit(BaseModel):
    """Schema for submitting P2H report"""
    vehicle_id: UUID
    details: List[P2HDetailSubmit] = Field(..., min_length=1, description="At least one checklist item required")
    
    @field_validator('details')
    @classmethod
    def validate_details(cls, v):
        """Validate that all details are provided"""
        if not v or len(v) == 0:
            raise ValueError('Minimal satu item checklist harus diisi')
        return v


class P2HReportResponse(BaseModel):
    """Schema for P2H report response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    vehicle_id: UUID
    user_id: UUID
    shift_number: int
    overall_status: InspectionStatus
    submission_date: date
    submission_time: time
    created_at: datetime
    details: List[P2HDetailResponse]


class P2HReportListResponse(BaseModel):
    """Schema for P2H report list (without details)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    vehicle: "VehicleResponse"
    user: "UserResponse"
    shift_number: int
    overall_status: InspectionStatus
    submission_date: date
    submission_time: time
    created_at: datetime


# Import for forward references
from app.schemas.vehicle import VehicleResponse
from app.schemas.user import UserResponse
P2HReportListResponse.model_rebuild()
