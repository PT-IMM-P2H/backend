from sqlalchemy import Column, String, Date, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base

# --- 1. ENUMS ---

class UserRole(str, enum.Enum):
    """3 Role Utama Sistem"""
    superadmin = "superadmin"
    admin = "admin"
    user = "user"  # Mencakup Karyawan IMM dan Driver Travel

class UserKategori(str, enum.Enum):
    """Pembeda entitas pengguna"""
    IMM = "IMM"
    TRAVEL = "TRAVEL"

# --- 2. MASTER DATA MODELS ---

class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_perusahaan = Column(String(100), nullable=False)
    status = Column(String(50)) # User, Driver, Driver Truk Sampah
    
    users = relationship("User", back_populates="company")
    vehicles = relationship("Vehicle", back_populates="company")

class Department(Base):
    __tablename__ = "departments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_department = Column(String(100), nullable=False)
    users = relationship("User", back_populates="department")

class Position(Base):
    __tablename__ = "positions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_posisi = Column(String(100), nullable=False)
    users = relationship("User", back_populates="position")

class WorkStatus(Base):
    __tablename__ = "work_statuses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_status = Column(String(50), nullable=False)
    users = relationship("User", back_populates="work_status")

# --- 3. USER MODEL ---

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    first_name = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    no_handphone = Column(String(20), nullable=True)
    
    # Foreign Keys
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id"), nullable=True)
    work_status_id = Column(UUID(as_uuid=True), ForeignKey("work_statuses.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    
    # Role & Kategori
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.user)
    kategori_pengguna = Column(SQLEnum(UserKategori), nullable=False, default=UserKategori.IMM)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="users")
    position = relationship("Position", back_populates="users")
    work_status = relationship("WorkStatus", back_populates="users")
    company = relationship("Company", back_populates="users")
    p2h_reports = relationship("P2HReport", back_populates="user")
    
    # Relasi ke Kendaraan
    vehicles_assigned = relationship("Vehicle", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"