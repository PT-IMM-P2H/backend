from sqlalchemy import Column, String, Integer, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models.vehicle import VehicleType


class ChecklistTemplate(Base):
    """Checklist template model for storing inspection items per vehicle type"""
    __tablename__ = "checklist_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False, index=True)
    section_name = Column(String(100), nullable=False)  # e.g., "Exterior", "Interior", "Engine"
    item_name = Column(String(200), nullable=False)  # e.g., "Ban kondisi baik"
    item_order = Column(Integer, nullable=False)  # Order of item in the checklist
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    p2h_details = relationship("P2HDetail", back_populates="checklist_item")
    
    def __repr__(self):
        return f"<ChecklistTemplate {self.vehicle_type} - {self.item_name}>"
