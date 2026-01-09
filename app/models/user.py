from sqlalchemy import Column, String, Date, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base
from app.models.mixins import SoftDeleteMixin

# --- 1. ENUMS ---

class UserRole(str, enum.Enum):
    """Role Utama Sistem P2H"""
    superadmin = "superadmin"
    admin = "admin"
    user = "user"

class UserKategori(str, enum.Enum):
    """Pembeda entitas untuk filter laporan (IMM vs Travel)"""
    IMM = "IMM"
    TRAVEL = "TRAVEL"

# --- 2. MASTER DATA MODELS ---

class Company(SoftDeleteMixin, Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_perusahaan = Column(String(100), nullable=False)
    status = Column(String(50)) # Contoh: User, Driver, Vendor
    
    users = relationship("User", back_populates="company")
    vehicles = relationship("Vehicle", back_populates="company")

class Department(SoftDeleteMixin, Base):
    __tablename__ = "departments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_department = Column(String(100), nullable=False)
    users = relationship("User", back_populates="department")

class Position(SoftDeleteMixin, Base):
    __tablename__ = "positions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_posisi = Column(String(100), nullable=False)
    users = relationship("User", back_populates="position")

class WorkStatus(SoftDeleteMixin, Base):
    __tablename__ = "work_statuses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_status = Column(String(50), nullable=False)
    users = relationship("User", back_populates="work_status")

# --- 3. FINALIZED USER MODEL ---

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    
    # Kredensial Login Utama (Sesuai arahan: Tanpa Username & First Name)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Metadata Profil
    birth_date = Column(Date, nullable=True) # Digunakan untuk password default DDMMYYYY
    
    # Foreign Keys Master Data (Menghubungkan ke tabel Master)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id"), nullable=True)
    work_status_id = Column(UUID(as_uuid=True), ForeignKey("work_statuses.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    
    # Role & Status
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.user)
    kategori_pengguna = Column(SQLEnum(UserKategori), nullable=False, default=UserKategori.IMM)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="users")
    position = relationship("Position", back_populates="users")
    work_status = relationship("WorkStatus", back_populates="users")
    company = relationship("Company", back_populates="users")
    p2h_reports = relationship("P2HReport", back_populates="user")
    vehicles_assigned = relationship("Vehicle", back_populates="user")

    def __repr__(self):
        # Menggunakan phone_number sebagai identitas unik di repr
        return f"<User {self.phone_number} - {self.full_name}>"