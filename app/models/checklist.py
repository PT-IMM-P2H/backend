from sqlalchemy import Column, String, Integer, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY  # Tambahkan ARRAY untuk tagging
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models.vehicle import VehicleType

class ChecklistTemplate(Base):
    """Checklist template model - Diperbarui tanpa menghapus kolom lama"""
    __tablename__ = "checklist_templates"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # --- KOLOM LAMA (Tetap dipertahankan agar tidak error) ---
    vehicle_type = Column(SQLEnum(VehicleType), nullable=True, index=True) 
    item_name = Column(String(200), nullable=False)  # Ini akan jadi 'text' di JSON
    
    # --- KOLOM BARU (Ditambahkan untuk mendukung Tagging & Shift) ---
    # NEW: Untuk menampung banyak tipe kendaraan (multi-centang di modal)
    vehicle_tags = Column(ARRAY(String), nullable=True, server_default='{}') 
    
    # NEW: Untuk menampung 5 macam shift (Shift 1, 2, 3, Long, No Shift)
    applicable_shifts = Column(ARRAY(String), nullable=True, server_default='{}')
    
    # NEW: Untuk menampung pilihan jawaban (seperti: Baik, Abnormal, atau Shift, Non-Shift)
    options = Column(ARRAY(String), nullable=True, server_default='{"Baik", "Abnormal"}')
    
    # --- KOLOM KONSISTENSI ---
    section_name = Column(String(100), nullable=False)
    item_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    p2h_details = relationship("P2HDetail", back_populates="checklist_item")
    
    def __repr__(self):
        return f"<ChecklistTemplate {self.item_name}>"