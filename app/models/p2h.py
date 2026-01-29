from sqlalchemy import Column, String, Integer, Date, Time, Boolean, Enum as SQLEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base

# --- 1. ENUMS ---

class InspectionStatus(str, enum.Enum):
    """Status hasil pemeriksaan per item atau secara keseluruhan"""
    NORMAL = "normal"
    WARNING = "warning"
    ABNORMAL = "abnormal"

class FinalStatus(str, enum.Enum):
    """Warna indikator untuk Dashboard/Sidebar"""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

# --- 2. MODELS ---

class P2HReport(Base):
    """
    Header Laporan P2H. 
    Menyimpan informasi utama siapa, kapan, dan kendaraan apa.
    """
    __tablename__ = "p2h_reports"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    shift_number = Column(Integer, nullable=False) # 1, 2, atau 3
    odometer = Column(Integer, nullable=True) # Nilai KM atau HM saat pemeriksaan
    overall_status = Column(SQLEnum(InspectionStatus), nullable=False)
    
    # Waktu submisi untuk reporting
    submission_date = Column(Date, nullable=False, index=True) 
    submission_time = Column(Time, nullable=False)
    
    # --- AUDIT TRAIL & SOFT DELETE ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="p2h_reports")
    user = relationship("User", back_populates="p2h_reports")
    details = relationship("P2HDetail", back_populates="report", cascade="all, delete-orphan")
    notifications = relationship("TelegramNotification", back_populates="report")

class P2HDetail(Base):
    """
    Detail Jawaban P2H.
    Menyimpan jawaban 'BAIK' atau 'RUSAK' untuk setiap poin pertanyaan.
    """
    __tablename__ = "p2h_details"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("p2h_reports.id", ondelete="CASCADE"), nullable=False)
    checklist_item_id = Column(UUID(as_uuid=True), ForeignKey("checklist_templates.id"), nullable=False)
    
    status = Column(SQLEnum(InspectionStatus), nullable=False) # Normal/Abnormal per item
    keterangan = Column(Text, nullable=True) # Catatan jika ada kerusakan
    image_url = Column(String, nullable=True) # Path foto bukti kerusakan jika ada
    
    is_deleted = Column(Boolean, default=False)

    # Relationships
    report = relationship("P2HReport", back_populates="details")
    checklist_item = relationship("ChecklistTemplate", back_populates="p2h_details")

class P2HDailyTracker(Base):
    """
    Tabel krusial untuk logika 'Merah/Kuning/Hijau' di Sidebar.
    Mencegah query berat ke p2h_reports untuk pengecekan status harian.
    """
    __tablename__ = "p2h_daily_tracker"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True) # Tanggal operasional
    
    # Status per shift
    shift_1_done = Column(Boolean, default=False)
    shift_1_report_id = Column(UUID(as_uuid=True), ForeignKey("p2h_reports.id"), nullable=True)
    
    shift_2_done = Column(Boolean, default=False)
    shift_2_report_id = Column(UUID(as_uuid=True), ForeignKey("p2h_reports.id"), nullable=True)
    
    shift_3_done = Column(Boolean, default=False)
    shift_3_report_id = Column(UUID(as_uuid=True), ForeignKey("p2h_reports.id"), nullable=True)
    
    # Status Akhir untuk Sidebar (Indikator Warna)
    final_status = Column(SQLEnum(FinalStatus), default=FinalStatus.RED)
    
    submission_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    vehicle = relationship("Vehicle", back_populates="daily_trackers")