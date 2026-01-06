from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from app.models.user import UserRole, UserKategori

# --- 1. USER BASE SCHEMA ---
class UserBase(BaseModel):
    """Schema dasar untuk data pengguna"""
    username: str = Field(..., min_length=5, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    full_name: str = Field(..., min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    no_handphone: Optional[str] = None
    
    # Menggunakan UserRole.user (lowercase sesuai dengan models/user.py)
    role: UserRole = Field(default=UserRole.user)
    kategori_pengguna: UserKategori = Field(default=UserKategori.IMM)
    is_active: bool = True

# --- 2. USER CREATE SCHEMA ---
class UserCreate(UserBase):
    """
    Schema untuk registrasi user baru.
    Menambahkan validasi password sesuai standar keamanan.
    """
    password: str = Field(
        ..., 
        min_length=8, 
        description="Password minimal 8 karakter, mengandung huruf besar, kecil, dan angka"
    )
    
    # Relasi ke Master Data (Tetap dipertahankan agar ID relasi masuk ke payload)
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    work_status_id: Optional[UUID] = None
    company_id: Optional[UUID] = None

# --- 3. USER UPDATE SCHEMA ---
class UserUpdate(BaseModel):
    """Schema untuk update data user (semua field optional)"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    no_handphone: Optional[str] = None
    role: Optional[UserRole] = None
    kategori_pengguna: Optional[UserKategori] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    work_status_id: Optional[UUID] = None
    company_id: Optional[UUID] = None

# --- 4. USER RESPONSE SCHEMA ---
class UserResponse(BaseModel):
    """
    Schema untuk output API. 
    Struktur ini akan dibungkus oleh base_response di controller/router.
    """
    id: UUID
    username: str
    full_name: str
    first_name: Optional[str]
    birth_date: Optional[date]
    no_handphone: Optional[str]
    role: UserRole
    kategori_pengguna: UserKategori
    is_active: bool
    
    department_id: Optional[UUID]
    position_id: Optional[UUID]
    company_id: Optional[UUID]
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- FORWARD REFERENCE ---
# Mencegah circular import agar LoginResponse mengenali UserResponse
from app.schemas.auth import LoginResponse
LoginResponse.model_rebuild()