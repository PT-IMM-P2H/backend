# app/models/__init__.py

from app.database import Base

# Import semua model agar terdaftar di Base.metadata
from app.models.user import User
from app.models.vehicle import Vehicle
# Jika file checklist Anda bernama checklist.py dan class-nya ChecklistTemplate
from app.models.checklist import ChecklistTemplate 
from app.models.p2h import (
    P2HReport, 
    P2HDetail, 
    P2HDailyTracker, 
    InspectionStatus, 
    FinalStatus
)

# Jika Anda memiliki model notifikasi (seperti yang ada di struktur folder Anda)
from app.models.notification import TelegramNotification

# __all__ memastikan bahwa saat kita import * dari models, 
# semua class ini akan ikut terbawa.
__all__ = [
    "Base",
    "User",
    "Vehicle",
    "ChecklistTemplate",
    "P2HReport",
    "P2HDetail",
    "P2HDailyTracker",
    "InspectionStatus",
    "FinalStatus",
    "TelegramNotification"
]