from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from app.models.user import UserRole, UserKategori

# --- NESTED SCHEMAS FOR RELATIONS ---
class CompanyResponse(BaseModel):
    id: UUID
    nama_perusahaan: str
    status: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class DepartmentResponse(BaseModel):
    id: UUID
    nama_department: str
    
    model_config = ConfigDict(from_attributes=True)

class PositionResponse(BaseModel):
    id: UUID
    nama_posisi: str
    
    model_config = ConfigDict(from_attributes=True)

class WorkStatusResponse(BaseModel):
    id: UUID
    nama_status: str
    
    model_config = ConfigDict(from_attributes=True)

# --- 1. USER BASE SCHEMA ---
class UserBase(BaseModel):
    """Schema dasar untuk data pengguna (Tanpa Username & First Name)"""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., description="Alamat email aktif")
    phone_number: str = Field(..., description="Nomor HP aktif (Kredensial Login)")
    birth_date: Optional[date] = None
    
    role: UserRole = Field(default=UserRole.user)
    kategori_pengguna: UserKategori = Field(default=UserKategori.IMM)
    is_active: bool = True

# --- 2. USER LOGIN SCHEMA ---
class UserLogin(BaseModel):
    """Skema login menggunakan Nomor HP sesuai arahan pembimbing"""
    phone_number: str = Field(..., description="Nomor HP yang terdaftar")
    password: str = Field(..., description="Password (Default: namadepanDDMMYYYY)")

# --- 3. USER CREATE SCHEMA ---
class UserCreate(UserBase):
    """
    Schema untuk registrasi user baru.
    Password sekarang opsional karena akan otomatis dibuatkan jika kosong
    dengan format: namadepanDDMMYYYY
    """
    password: Optional[str] = Field(None, min_length=8)
    
    # Relasi ke Master Data PT. IMM
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    work_status_id: Optional[UUID] = None
    company_id: Optional[UUID] = None

# --- 4. USER UPDATE SCHEMA ---
class UserUpdate(BaseModel):
    """Schema untuk update data user (semua field optional)"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    role: Optional[UserRole] = None
    kategori_pengguna: Optional[UserKategori] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    work_status_id: Optional[UUID] = None
    company_id: Optional[UUID] = None

# --- 5. USER RESPONSE SCHEMA ---
class UserResponse(BaseModel):
    """
    Schema untuk output API terstandarisasi.
    """
    id: UUID
    full_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    role: UserRole
    kategori_pengguna: UserKategori
    is_active: bool
    
    # Metadata Relasi (IDs)
    department_id: Optional[UUID]
    position_id: Optional[UUID]
    work_status_id: Optional[UUID]
    company_id: Optional[UUID]
    
    # Nested Relations (Objects)
    company: Optional[CompanyResponse] = None
    department: Optional[DepartmentResponse] = None
    position: Optional[PositionResponse] = None
    work_status: Optional[WorkStatusResponse] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- FORWARD REFERENCE ---
# Mencegah circular import agar LoginResponse mengenali UserResponse
from app.schemas.auth import LoginResponse
LoginResponse.model_rebuild()