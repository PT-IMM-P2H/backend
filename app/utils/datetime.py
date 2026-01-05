from datetime import datetime, date, time, timedelta
import pytz
from app.config import settings

def get_current_datetime() -> datetime:
    """Mendapatkan waktu sekarang sesuai timezone Asia/Makassar (WITA)"""
    tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(tz)

def get_current_date() -> date:
    """
    [LOGIKA OPERASIONAL SITE] 
    Mendapatkan tanggal operasional. 
    Jika waktu < 05:00 pagi, maka dianggap masih tanggal hari sebelumnya.
    """
    now = get_current_datetime()
    # Jika jam sekarang antara 00:00 sampai 04:59
    if now.hour < 5:
        return (now - timedelta(days=1)).date()
    return now.date()

def get_current_time() -> time:
    """Mendapatkan jam sekarang (tanpa tanggal)"""
    return get_current_datetime().time()

def get_shift_number(current_time: time = None) -> int:
    """
    Menentukan shift berdasarkan jam kerja PT. IMM:
    - Shift 1: 06:00 - 14:00
    - Shift 2: 14:00 - 22:00
    - Shift 3: 22:00 - 06:00
    """
    if current_time is None:
        current_time = get_current_time()
        
    now_hour = current_time.hour
    
    if 6 <= now_hour < 14:
        return 1
    elif 14 <= now_hour < 22:
        return 2
    else:
        # Jam 22:00 sampai 05:59 masuk Shift 3
        return 3

def days_until_expiry(expiry_date: date) -> int:
    """
    [PENTING UNTUK SCHEDULER]
    Menghitung sisa hari menuju tanggal kadaluarsa (STNK/KIR).
    Digunakan oleh scheduler untuk mengirim alert ke Telegram.
    """
    if not expiry_date:
        return 999 # Jika tidak ada tanggal, dianggap masih lama
        
    today = get_current_date()
    delta = expiry_date - today
    return delta.days