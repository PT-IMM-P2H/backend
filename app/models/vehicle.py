from sqlalchemy import Column, String, Date, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base

class VehicleType(enum.Enum):
    """Tipe kendaraan yang tersedia di sistem"""
    LIGHT_VEHICLE = "Light Vehicle"
    ELECTRIC_VEHICLE = "Electric Vehicle"
    DOUBLE_CABIN = "Double Cabin"
    SINGLE_CABIN = "Single Cabin"
    BUS = "Bus"
    AMBULANCE = "Ambulance"
    FIRE_TRUCK = "Fire Truck"
    KOMANDO = "Komando"
    TRUK_SAMPAH = "Truk Sampah"


    
class ShiftType(enum.Enum):
    SHIFT = "shift"
    NON_SHIFT = "non_shift"

class UnitKategori(enum.Enum):
    IMM = "IMM"
    TRAVEL = "TRAVEL"

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    no_lambung = Column(String(50), unique=True, nullable=True, index=True)
    warna_no_lambung = Column(String(20), nullable=True)
    plat_nomor = Column(String(20), nullable=False, index=True)
    vehicle_type = Column(SQLEnum(VehicleType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    merk = Column(String(100), nullable=True)
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    no_rangka = Column(String(100), nullable=True)
    no_mesin = Column(String(100), nullable=True)
    stnk_expiry = Column(Date, nullable=True)
    pajak_expiry = Column(Date, nullable=True)
    kir_expiry = Column(Date, nullable=True)
    
    kategori_unit = Column(SQLEnum(UnitKategori), nullable=False, default=UnitKategori.IMM)
    shift_type = Column(SQLEnum(ShiftType), nullable=False, default=ShiftType.SHIFT)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="vehicles")
    user = relationship("User", back_populates="vehicles_assigned")
    p2h_reports = relationship("P2HReport", back_populates="vehicle")
    daily_trackers = relationship("P2HDailyTracker", back_populates="vehicle")
    
    # Referensi string harus tepat dengan nama kelas di notification.py
    notifications = relationship("TelegramNotification", back_populates="vehicle")