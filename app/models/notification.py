from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class NotificationType(str, enum.Enum):
    """
    Tipe notifikasi yang didukung oleh sistem.
    Sesuai dengan logika di TelegramService dan Scheduler Jobs.
    """
    P2H_ABNORMAL = "p2h_abnormal"
    P2H_WARNING = "p2h_warning"
    STNK_EXPIRY = "stnk_expiry"
    KIR_EXPIRY = "kir_expiry"


class TelegramNotification(Base):
    """
    Model untuk mencatat setiap pesan yang dikirim (atau gagal dikirim) ke Telegram.
    Berfungsi sebagai audit log untuk memastikan alert sampai ke stakeholder.
    """
    __tablename__ = "telegram_notifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Indikator jenis pesan (Alert P2H atau Alert Dokumen)
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    
    # Relasi ke Kendaraan (UUID)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True, index=True)
    
    # Relasi ke Laporan P2H (UUID) - Null jika ini adalah notifikasi Expired Dokumen
    report_id = Column(UUID(as_uuid=True), ForeignKey("p2h_reports.id"), nullable=True)
    
    # Isi pesan yang dikirimkan ke Telegram
    message = Column(Text, nullable=False)
    
    # Status Pengiriman
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True) # Kapan pesan berhasil terkirim
    error_message = Column(Text, nullable=True) # Catatan jika terjadi error (misal: bot diblokir)
    
    # Audit Trail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # --- RELATIONSHIPS ---
    # Sesuai dengan back_populates di model Vehicle dan P2HReport
    vehicle = relationship("Vehicle", back_populates="notifications")
    report = relationship("P2HReport", back_populates="notifications")
    
    def __repr__(self):
        return f"<TelegramNotification {self.notification_type} - Sent: {self.is_sent} - Unit: {self.vehicle_id}>"