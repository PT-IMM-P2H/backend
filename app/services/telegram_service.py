from typing import Optional
import logging
from datetime import datetime
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.notification import TelegramNotification, NotificationType
from app.models.vehicle import Vehicle
from app.models.p2h import P2HReport, InspectionStatus

logger = logging.getLogger(__name__)

class TelegramService:
    """Service for sending Telegram notifications for P2H and Expiry Alerts"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_message(self, message: str) -> bool:
        """Kirim pesan ke Telegram menggunakan mode HTML"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ Telegram message sent successfully")
                    return True
                else:
                    logger.error(f"❌ Telegram API Error: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error connection to Telegram: {str(e)}")
            return False
    
    def format_p2h_notification(
        self,
        vehicle: Vehicle,
        report: P2HReport,
        status: InspectionStatus
    ) -> str:
        """Format pesan untuk laporan P2H yang bermasalah (Abnormal/Warning)"""
        status_emoji = "❌" if status == InspectionStatus.ABNORMAL else "⚠️"
        status_text = "ABNORMAL (STOP OPERASI)" if status == InspectionStatus.ABNORMAL else "WARNING (PERLU PERBAIKAN)"
        
        # Ambil list item yang abnormal jika ada (opsional, bisa dikembangkan nanti)
        message = f"""
{status_emoji} <b>P2H ALERT: {status_text}</b>
━━━━━━━━━━━━━━━━━━━━
<b>Unit:</b> <code>{vehicle.no_lambung}</code>
<b>Tipe:</b> {vehicle.vehicle_type.value}
<b>Merk/Plat:</b> {vehicle.merk or '-'} / {vehicle.plat_nomor or '-'}

<b>📅 Detail Pemeriksaan:</b>
<b>Tanggal:</b> {report.submission_date.strftime('%d %b %Y')}
<b>Waktu:</b> {report.submission_time.strftime('%H:%M')} WITA
<b>Shift:</b> {report.shift_number}
<b>User:</b> {report.user.full_name if report.user else 'System'}

<b>📝 Status Akhir:</b> {status.value.upper()}

<b>⚠️ Tindakan:</b> 
Harap segera melakukan pengecekan unit di workshop terdekat.
━━━━━━━━━━━━━━━━━━━━
<i>Sistem P2H Digital PT. IMM</i>
        """
        return message.strip()
    
    def format_expiry_notification(
        self,
        vehicle: Vehicle,
        expiry_type: str,
        expiry_date: datetime,
        days_remaining: int
    ) -> str:
        """Format pesan untuk peringatan STNK/KIR yang akan habis"""
        if days_remaining <= 0:
            urgency = "🚨 <b>SUDAH EXPIRED (STOP OPERASI)</b>"
            emoji = "🚫"
        elif days_remaining <= 7:
            urgency = "🔴 <b>SANGAT SEGERA</b>"
            emoji = "🚨"
        else:
            urgency = "🟡 <b>PERINGATAN</b>"
            emoji = "⚠️"

        message = f"""
{emoji} <b>EXPIRY ALERT: {expiry_type}</b>
━━━━━━━━━━━━━━━━━━━━
<b>Unit:</b> <code>{vehicle.no_lambung}</code>
<b>Plat Nomor:</b> {vehicle.plat_nomor or '-'}

<b>📅 Detail Dokumen:</b>
<b>Jenis:</b> {expiry_type}
<b>Tanggal Expired:</b> {expiry_date.strftime('%d/%m/%Y')}
<b>Sisa Waktu:</b> <b>{days_remaining} Hari Lagi</b>

<b>Status:</b> {urgency}

<b>💡 Info:</b>
Harap segera memproses perpanjangan dokumen agar operasional tidak terganggu.
━━━━━━━━━━━━━━━━━━━━
<i>Sistem Monitoring Asset PT. IMM</i>
        """
        return message.strip()
    
    async def send_p2h_notification(
        self,
        db: Session,
        vehicle: Vehicle,
        report: P2HReport,
        status: InspectionStatus
    ) -> Optional[TelegramNotification]:
        """Kirim notifikasi P2H dan catat di tabel telegram_notifications"""
        
        if status == InspectionStatus.NORMAL:
            return None
            
        notification_type = (
            NotificationType.P2H_ABNORMAL 
            if status == InspectionStatus.ABNORMAL 
            else NotificationType.P2H_WARNING
        )
        
        message = self.format_p2h_notification(vehicle, report, status)
        
        # Simpan log ke DB
        notification = TelegramNotification(
            notification_type=notification_type,
            vehicle_id=vehicle.id,
            report_id=report.id,
            message=message,
            is_sent=False
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Kirim
        success = await self.send_message(message)
        
        # Update status kirim
        notification.is_sent = success
        if success:
            notification.sent_at = datetime.utcnow()
        else:
            notification.error_message = "Gagal terhubung ke Telegram API"
        
        db.commit()
        return notification
    
    async def send_expiry_notification(
        self,
        db: Session,
        vehicle: Vehicle,
        expiry_type: str,
        expiry_date: datetime,
        days_remaining: int
    ) -> Optional[TelegramNotification]:
        """Kirim notifikasi Expired dan catat di database"""
        
        notification_type = (
            NotificationType.STNK_EXPIRY 
            if expiry_type == "STNK" 
            else NotificationType.KIR_EXPIRY
        )
        
        message = self.format_expiry_notification(
            vehicle, expiry_type, expiry_date, days_remaining
        )
        
        notification = TelegramNotification(
            notification_type=notification_type,
            vehicle_id=vehicle.id,
            message=message,
            is_sent=False
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        success = await self.send_message(message)
        
        notification.is_sent = success
        if success:
            notification.sent_at = datetime.utcnow()
        else:
            notification.error_message = "Gagal kirim alert expired"
            
        db.commit()
        return notification

# Global instance
telegram_service = TelegramService()