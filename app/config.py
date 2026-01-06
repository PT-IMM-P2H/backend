from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

# Get the backend directory path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Telegram (Optional - will be disabled if not configured)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Application
    APP_NAME: str = "P2H System PT. IMM"
    APP_VERSION: str = "1.0.0"
    TIMEZONE: str = "Asia/Makassar"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()
