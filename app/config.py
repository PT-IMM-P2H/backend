from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 jam
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Application
    APP_NAME: str = "P2H System PT. IMM"
    APP_VERSION: str = "1.0.0"
    TIMEZONE: str = "Asia/Makassar" # WITA - Sesuai lokasi Bontang
    
    # CORS - Support both JSON array and comma-separated string
    CORS_ORIGINS: str = '["http://localhost:5173","http://127.0.0.1:5173","http://localhost:8000","http://127.0.0.1:8000"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from JSON array or comma-separated string"""
        import json
        try:
            # Try parsing as JSON array first
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            # Fallback to comma-separated string
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

settings = Settings()