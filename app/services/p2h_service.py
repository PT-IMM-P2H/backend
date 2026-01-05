from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Tuple, List
from uuid import UUID
import logging

from app.models.user import User
from app.models.p2h import P2HReport, P2HDetail, P2HDailyTracker, InspectionStatus
from app.models.vehicle import Vehicle, ShiftType
from app.models.checklist import ChecklistTemplate
from app.schemas.p2h import P2HReportSubmit, P2HDetailSubmit
from app.utils.datetime import get_current_date, get_current_time, get_shift_number
from app.services.telegram_service import telegram_service

logger = logging.getLogger(__name__)

class P2HService:
    """Service for P2H (Pelaksanaan Pemeriksaan Harian) operations"""
    
    @staticmethod
    def get_or_create_daily_tracker(db: Session, vehicle_id: UUID, current_date) -> P2HDailyTracker:
        """
        Mendapatkan atau membuat tracker harian untuk unit tertentu.
        """
        tracker = db.query(P2HDailyTracker).filter(
            and_(
                P2HDailyTracker.vehicle_id == vehicle_id,
                P2HDailyTracker.date == current_date
            )
        ).first()
        
        if not tracker:
            tracker = P2HDailyTracker(
                vehicle_id=vehicle_id,
                date=current_date,
                submission_count=0
            )
            db.add(tracker)
            db.commit()
            db.refresh(tracker)
        
        return tracker
    
    @staticmethod
    def can_submit_p2h(
        db: Session,
        vehicle: Vehicle,
        shift_number: int
    ) -> Tuple[bool, str]:
        """
        Validasi apakah unit boleh mengisi P2H pada shift saat ini.
        """
        current_date = get_current_date()
        tracker = P2HService.get_or_create_daily_tracker(db, vehicle.id, current_date)
        
        # Logika Kendaraan Non-Shift (Hanya 1x sehari)
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            if tracker.shift_1_done:
                return False, "P2H sudah diisi hari ini untuk kendaraan non-shift"
            return True, "P2H dapat diisi"
        
        # Logika Kendaraan Shift (Hanya 1x per nomor shift)
        shift_status = {
            1: tracker.shift_1_done,
            2: tracker.shift_2_done,
            3: tracker.shift_3_done
        }
        
        if shift_status.get(shift_number):
            return False, f"P2H shift {shift_number} sudah diisi untuk unit ini hari ini"
        
        return True, "P2H dapat diisi"
    
    @staticmethod
    def calculate_overall_status(details: List[P2HDetailSubmit]) -> InspectionStatus:
        """
        Menentukan status akhir P2H berdasarkan item yang diperiksa.
        Prioritas: ABNORMAL > WARNING > NORMAL
        """
        statuses = [d.status for d in details]
        
        if InspectionStatus.ABNORMAL in statuses:
            return InspectionStatus.ABNORMAL
        if InspectionStatus.WARNING in statuses:
            return InspectionStatus.WARNING
        return InspectionStatus.NORMAL
    
    @staticmethod
    async def submit_p2h(
        db: Session,
        user: User,
        submission: P2HReportSubmit
    ) -> P2HReport:
        """
        Memproses submit form P2H dari user.
        """
        # 1. Cari Vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.id == submission.vehicle_id).first()
        if not vehicle:
            raise ValueError("Kendaraan tidak ditemukan")
        if not vehicle.is_active:
            raise ValueError("Kendaraan sedang dalam status non-aktif")
        
        # 2. Ambil Waktu Operasional (Reset jam 05:00)
        current_date = get_current_date()
        current_time = get_current_time()
        shift_number = get_shift_number(current_time)
        
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            shift_number = 1
        
        # 3. Cek Quota/Izin Submit
        can_submit, message = P2HService.can_submit_p2h(db, vehicle, shift_number)
        if not can_submit:
            raise ValueError(message)
        
        # 4. Hitung Status Keseluruhan
        overall_status = P2HService.calculate_overall_status(submission.details)
        
        # 5. Simpan Header Laporan
        report = P2HReport(
            vehicle_id=vehicle.id,
            user_id=user.id,
            shift_number=shift_number,
            overall_status=overall_status,
            submission_date=current_date,
            submission_time=current_time
        )
        db.add(report)
        db.flush() # Ambil ID report untuk detail
        
        # 6. Simpan Detail Pemeriksaan
        for d in submission.details:
            detail = P2HDetail(
                report_id=report.id,
                checklist_item_id=d.checklist_item_id,
                status=d.status,
                keterangan=d.keterangan
            )
            db.add(detail)
        
        # 7. Update Daily Tracker
        tracker = P2HService.get_or_create_daily_tracker(db, vehicle.id, current_date)
        tracker.submission_count += 1
        
        if shift_number == 1 or vehicle.shift_type == ShiftType.NON_SHIFT:
            tracker.shift_1_done = True
            tracker.shift_1_report_id = report.id
        elif shift_number == 2:
            tracker.shift_2_done = True
            tracker.shift_2_report_id = report.id
        elif shift_number == 3:
            tracker.shift_3_done = True
            tracker.shift_3_report_id = report.id
        
        db.commit()
        db.refresh(report)
        
        # 8. Notifikasi Telegram (Hanya jika bermasalah)
        if overall_status in [InspectionStatus.ABNORMAL, InspectionStatus.WARNING]:
            try:
                await telegram_service.send_p2h_notification(
                    db, vehicle, report, overall_status
                )
            except Exception as e:
                logger.error(f"Telegram alert failed: {str(e)}")
        
        return report

    @staticmethod
    def get_vehicle_p2h_status(db: Session, vehicle_id: UUID) -> dict:
        """
        Cek status warna (Merah/Hijau/Kuning) untuk unit di dashboard/scan.
        """
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError("Unit tidak terdaftar")
            
        current_date = get_current_date()
        current_time = get_current_time()
        shift_number = get_shift_number(current_time)
        
        tracker = db.query(P2HDailyTracker).filter(
            and_(
                P2HDailyTracker.vehicle_id == vehicle_id,
                P2HDailyTracker.date == current_date
            )
        ).first()
        
        # Status default jika belum ada tracker sama sekali hari ini
        shifts_done = {1: False, 2: False, 3: False}
        if tracker:
            shifts_done = {
                1: tracker.shift_1_done,
                2: tracker.shift_2_done,
                3: tracker.shift_3_done
            }
            
        # Tentukan status warna untuk Frontend
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            p2h_done = shifts_done[1]
            color = "green" if p2h_done else "red"
        else:
            current_done = shifts_done.get(shift_number, False)
            all_done = all(shifts_done.values())
            if all_done:
                color = "green"
            elif any(shifts_done.values()):
                color = "yellow"
            else:
                color = "red"
        
        return {
            "no_lambung": vehicle.no_lambung,
            "current_shift": shift_number if vehicle.shift_type == ShiftType.SHIFT else 1,
            "status_p2h": "Lengkap" if color == "green" else "Belum Lengkap",
            "color_code": color,
            "shifts_completed": [s for s, done in shifts_done.items() if done]
        }

p2h_service = P2HService()