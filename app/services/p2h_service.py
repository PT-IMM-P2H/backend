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
from app.utils.datetime import (
    get_current_date_shift, 
    get_current_date_non_shift,
    get_current_time, 
    get_shift_number, 
    get_long_shift_number, 
    is_within_non_shift_hours
)
from app.services.telegram_service import telegram_service

logger = logging.getLogger(__name__)

class P2HService:
    """Service for P2H (Pelaksanaan Pemeriksaan Harian) operations"""
    
    @staticmethod
    def get_or_create_daily_tracker(db: Session, vehicle: Vehicle, current_date) -> P2HDailyTracker:
        """
        Mendapatkan atau membuat tracker harian untuk unit tertentu.
        Menggunakan tanggal yang sudah disesuaikan dengan tipe shift.
        """
        tracker = db.query(P2HDailyTracker).filter(
            and_(
                P2HDailyTracker.vehicle_id == vehicle.id,
                P2HDailyTracker.date == current_date
            )
        ).first()
        
        if not tracker:
            tracker = P2HDailyTracker(
                vehicle_id=vehicle.id,
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
        selected_shift: int  # Shift yang dipilih user dari dropdown
    ) -> Tuple[bool, str]:
        """
        Validasi apakah unit boleh mengisi P2H pada shift yang dipilih.
        
        Rules:
        - SHIFT (Kuning): 3x sehari, reset jam 05:00, validasi shift vs jam saat ini
        - NON_SHIFT (Hijau/Biru): 1x sehari, reset jam 00:00, hanya jam 06:00-16:00
        - LONG_SHIFT: 2x sehari, reset jam 05:00, validasi shift vs jam saat ini
        """
        current_time = get_current_time()
        
        # Tentukan tanggal operasional berdasarkan tipe shift
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            current_date = get_current_date_non_shift()  # Reset jam 00:00
        else:
            current_date = get_current_date_shift()  # Reset jam 05:00
        
        tracker = P2HService.get_or_create_daily_tracker(db, vehicle, current_date)
        
        # Logika Kendaraan Non-Shift (Hijau & Biru - Hanya 1x sehari, jam 06:00-16:00)
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            # Validasi jam kerja non-shift
            if not is_within_non_shift_hours(current_time):
                return False, "P2H non-shift hanya dapat diisi pada jam 06:00-16:00"
            
            if tracker.shift_1_done:
                return False, "P2H sudah diisi hari ini untuk kendaraan non-shift"
            return True, "P2H dapat diisi"
        
        # Logika Kendaraan Long Shift (2x sehari, reset jam 05:00)
        if vehicle.shift_type == ShiftType.LONG_SHIFT:
            actual_long_shift = get_long_shift_number(current_time)
            
            # Validasi: Shift yang dipilih harus sesuai dengan jam saat ini
            if selected_shift != actual_long_shift:
                return False, f"Saat ini adalah Long Shift {actual_long_shift} (bukan Long Shift {selected_shift}). Pilih shift yang sesuai."
            
            if selected_shift == 1:
                if tracker.shift_1_done:
                    return False, "P2H long shift 1 (06:00-19:00) sudah diisi hari ini"
            else:  # selected_shift == 2
                if tracker.shift_2_done:
                    return False, "P2H long shift 2 (18:00-07:00) sudah diisi hari ini"
            return True, "P2H dapat diisi"
        
        # Logika Kendaraan Shift (Kuning - 3x sehari, reset jam 05:00)
        actual_shift = get_shift_number(current_time)
        
        # Validasi: Shift yang dipilih harus sesuai dengan jam saat ini
        if selected_shift != actual_shift:
            return False, f"Saat ini adalah Shift {actual_shift} (bukan Shift {selected_shift}). Pilih shift yang sesuai dengan jam saat ini."
        
        shift_status = {
            1: tracker.shift_1_done,
            2: tracker.shift_2_done,
            3: tracker.shift_3_done
        }
        
        if shift_status.get(selected_shift):
            return False, f"P2H shift {selected_shift} sudah diisi untuk unit ini hari ini"
        
        return True, "P2H dapat diisi"
    
    @staticmethod
    def calculate_overall_status(details: List[P2HDetailSubmit]) -> InspectionStatus:
        """
        Menentukan status akhir P2H berdasarkan item yang diperiksa.
        Prioritas: WARNING > ABNORMAL > NORMAL
        
        Logic:
        - Jika ada WARNING, maka overall = WARNING
        - Jika tidak ada WARNING tapi ada ABNORMAL, maka overall = ABNORMAL
        - Jika semua NORMAL, maka overall = NORMAL
        """
        statuses = [d.status for d in details]
        
        # Prioritas 1: WARNING (paling kritis)
        if InspectionStatus.WARNING in statuses:
            return InspectionStatus.WARNING
        
        # Prioritas 2: ABNORMAL
        if InspectionStatus.ABNORMAL in statuses:
            return InspectionStatus.ABNORMAL
        
        # Default: NORMAL
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
        logger.info(f"📝 Starting P2H submission for vehicle_id: {submission.vehicle_id}, user: {user.full_name}")
        
        # 1. Cari Vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.id == submission.vehicle_id).first()
        if not vehicle:
            raise ValueError("Kendaraan tidak ditemukan")
        if not vehicle.is_active:
            raise ValueError("Kendaraan sedang dalam status non-aktif")
        
        logger.info(f"🚗 Vehicle found: {vehicle.no_lambung}")
        
        # 2. Ambil Waktu Operasional
        current_time = get_current_time()
        
        # Tentukan tanggal operasional berdasarkan tipe shift
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            current_date = get_current_date_non_shift()  # Reset jam 00:00
        else:
            current_date = get_current_date_shift()  # Reset jam 05:00
        
        # Tentukan shift number berdasarkan tipe kendaraan dan submission
        # submission.shift_number adalah shift yang dipilih user dari dropdown
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            shift_number = 1  # Non-shift selalu shift 1
        elif vehicle.shift_type == ShiftType.LONG_SHIFT:
            shift_number = submission.shift_number or get_long_shift_number(current_time)
        else:  # SHIFT
            shift_number = submission.shift_number or get_shift_number(current_time)
        
        # 3. Cek Quota/Izin Submit dengan validasi shift yang dipilih
        can_submit, message = P2HService.can_submit_p2h(db, vehicle, shift_number)
        if not can_submit:
            raise ValueError(message)
        
        # 4. Hitung Status Keseluruhan
        overall_status = P2HService.calculate_overall_status(submission.details)
        logger.info(f"📊 Overall status calculated: {overall_status}")
        
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
        
        logger.info(f"💾 P2H Report created with ID: {report.id}")
        
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
        tracker = P2HService.get_or_create_daily_tracker(db, vehicle, current_date)
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
        logger.info(f"🔔 Checking if telegram notification needed - Status: {overall_status}")
        if overall_status in [InspectionStatus.ABNORMAL, InspectionStatus.WARNING]:
            try:
                logger.info(f"📤 Sending telegram notification for report {report.id}")
                notification = await telegram_service.send_p2h_notification(
                    db, vehicle, report, overall_status
                )
                if notification and notification.is_sent:
                    logger.info(f"✅ Telegram notification sent successfully")
                else:
                    logger.warning(f"⚠️ Telegram notification failed to send")
            except Exception as e:
                logger.error(f"❌ Telegram alert failed: {str(e)}", exc_info=True)
        else:
            logger.info(f"ℹ️ No telegram notification needed - Status is NORMAL")
        
        return report

    @staticmethod
    def get_vehicle_p2h_status(db: Session, vehicle_id: UUID) -> dict:
        """
        Cek status warna (Merah/Hijau/Kuning) untuk unit di dashboard/scan.
        
        Color Logic:
        - SHIFT (Kuning): Hijau jika semua shift done, Kuning jika sebagian, Merah jika kosong
        - NON_SHIFT (Hijau/Biru): Hijau jika done, Merah jika belum
        - LONG_SHIFT: Hijau jika kedua shift done, Kuning jika 1 done, Merah jika kosong
        """
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError("Unit tidak terdaftar")
        
        current_time = get_current_time()
        
        # Gunakan tanggal operasional yang sesuai dengan tipe shift
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            current_date = get_current_date_non_shift()  # Reset jam 00:00
        else:
            current_date = get_current_date_shift()  # Reset jam 05:00
        
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
        
        # Tentukan shift number dan status warna
        if vehicle.shift_type == ShiftType.NON_SHIFT:
            shift_number = 1
            p2h_done = shifts_done[1]
            color = "green" if p2h_done else "red"
            shifts_completed = [1] if p2h_done else []
            
        elif vehicle.shift_type == ShiftType.LONG_SHIFT:
            shift_number = get_long_shift_number(current_time)
            shift_1_done = shifts_done[1]
            shift_2_done = shifts_done[2]
            
            if shift_1_done and shift_2_done:
                color = "green"  # Semua long shift selesai
            elif shift_1_done or shift_2_done:
                color = "yellow"  # Sebagian selesai
            else:
                color = "red"  # Belum ada yang selesai
            
            shifts_completed = [s for s in [1, 2] if shifts_done[s]]
            
        else:  # SHIFT (3x sehari)
            shift_number = get_shift_number(current_time)
            all_done = shifts_done[1] and shifts_done[2] and shifts_done[3]
            any_done = shifts_done[1] or shifts_done[2] or shifts_done[3]
            
            if all_done:
                color = "green"
            elif any_done:
                color = "yellow"
            else:
                color = "red"
            
            shifts_completed = [s for s in [1, 2, 3] if shifts_done[s]]
        
        return {
            "no_lambung": vehicle.no_lambung,
            "warna_no_lambung": vehicle.warna_no_lambung,
            "shift_type": vehicle.shift_type.value,
            "current_shift": shift_number,
            "status_p2h": "Lengkap" if color == "green" else "Belum Lengkap",
            "color_code": color,
            "shifts_completed": shifts_completed
        }

p2h_service = P2HService()