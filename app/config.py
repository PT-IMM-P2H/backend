from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Don't load .env file if running on Railway
        # Railway sets RAILWAY_ENVIRONMENT_NAME (e.g., "production")
        env_file=".env" if os.getenv("RAILWAY_ENVIRONMENT_NAME") is None else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    PORT: int = 8000

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # Application
    APP_NAME: str = "P2H System PT. IMM"
    APP_VERSION: str = "1.0.0"
    TIMEZONE: str = "Asia/Makassar" # WITA - Sesuai lokasi Bontang
    
    # CORS - Support both JSON array and comma-separated string
    CORS_ORIGINS: str = '["http://localhost:5173","http://127.0.0.1:5173"]'
    
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
    
    def is_origin_allowed(self, origin: str) -> bool:
        """
        Check if origin is allowed, supporting wildcard patterns.
        Examples:
        - https://*.vercel.app matches https://p2h-xyz.vercel.app
        - https://*.railway.app matches any Railway deployment
        """
        import re
        
        for allowed_origin in self.cors_origins_list:
            # Exact match
            if allowed_origin == origin:
                return True
            
            # Wildcard match (convert * to regex)
            if "*" in allowed_origin:
                pattern = allowed_origin.replace(".", r"\.").replace("*", ".*")
                if re.match(f"^{pattern}$", origin):
                    return True
        
        return False
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

settings = Settings()