"""
Application Constants
Centralized constants for the entire backend application
"""

# HTTP Status Codes (for consistency)
class HTTPStatus:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


# API Response Messages
class ResponseMessages:
    # Success Messages
    SUCCESS = "Operasi berhasil"
    CREATED = "Data berhasil dibuat"
    UPDATED = "Data berhasil diperbarui"
    DELETED = "Data berhasil dihapus"
    
    # Error Messages
    NOT_FOUND = "Data tidak ditemukan"
    INVALID_DATA = "Data tidak valid"
    UNAUTHORIZED = "Tidak terautentikasi"
    FORBIDDEN = "Tidak memiliki akses"
    DUPLICATE_ENTRY = "Data sudah ada"
    INTERNAL_ERROR = "Terjadi kesalahan pada server"
    
    # Auth Messages
    LOGIN_SUCCESS = "Login berhasil"
    LOGIN_FAILED = "Email atau password salah"
    LOGOUT_SUCCESS = "Logout berhasil"
    TOKEN_EXPIRED = "Token telah kadaluarsa"
    TOKEN_INVALID = "Token tidak valid"
    
    # P2H Messages
    P2H_SUBMITTED = "Laporan P2H berhasil dikirim"
    P2H_UPDATED = "Laporan P2H berhasil diperbarui"
    P2H_NOT_FOUND = "Laporan P2H tidak ditemukan"
    
    # User Messages
    USER_CREATED = "Pengguna berhasil dibuat"
    USER_UPDATED = "Pengguna berhasil diperbarui"
    USER_DELETED = "Pengguna berhasil dihapus"
    USER_NOT_FOUND = "Pengguna tidak ditemukan"
    
    # Vehicle Messages
    VEHICLE_CREATED = "Kendaraan berhasil dibuat"
    VEHICLE_UPDATED = "Kendaraan berhasil diperbarui"
    VEHICLE_DELETED = "Kendaraan berhasil dihapus"
    VEHICLE_NOT_FOUND = "Kendaraan tidak ditemukan"


# Pagination
class Pagination:
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


# Date/Time Formats
class DateFormats:
    ISO_DATE = "%Y-%m-%d"
    ISO_DATETIME = "%Y-%m-%d %H:%M:%S"
    DISPLAY_DATE = "%d/%m/%Y"
    DISPLAY_DATETIME = "%d/%m/%Y %H:%M"
    MONTH_YEAR = "%Y-%m"


# Indonesian Month Names
MONTH_NAMES_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]


# File Upload Settings
class FileUploadSettings:
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]
    ALLOWED_DOCUMENT_EXTENSIONS = [".pdf"]
    UPLOAD_DIR = "uploads"


# Password Settings
class PasswordSettings:
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = False


# Token Settings (Override with environment variables)
class TokenSettings:
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7


# Database Settings
class DatabaseSettings:
    POOL_SIZE = 5
    MAX_OVERFLOW = 10
    POOL_RECYCLE = 3600  # 1 hour
    POOL_PRE_PING = True


# Telegram Notification Settings
class TelegramSettings:
    MAX_MESSAGE_LENGTH = 4096
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # seconds


# P2H Report Settings
class P2HSettings:
    # Berapa hari data P2H yang ditampilkan di dashboard (default)
    DEFAULT_DAYS_RANGE = 30
    
    # Auto-generate P2H schedule setiap jam berapa (24-hour format)
    AUTO_GENERATE_HOUR = 6  # 06:00 AM
    
    # Maximum items per P2H checklist
    MAX_CHECKLIST_ITEMS = 100


# Cache Settings (if using Redis)
class CacheSettings:
    DEFAULT_TTL = 300  # 5 minutes
    STATISTICS_TTL = 600  # 10 minutes
    USER_DATA_TTL = 1800  # 30 minutes


# Logging Settings
class LogSettings:
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE = "app.log"
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5


# Application Info
class AppInfo:
    NAME = "P2H System"
    VERSION = "1.0.0"
    DESCRIPTION = "Sistem Pemeriksaan Kendaraan Sebelum Operasi (P2H)"
    API_PREFIX = ""  # No prefix, direct access from root
