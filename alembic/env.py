from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os
from pathlib import Path

# 1. Pastikan path mengarah ke root directory (backend) agar modul 'app' terbaca
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database import Base

# 2. IMPORT SEMUA MODEL DI SINI
# Ini sangat penting agar Alembic mendeteksi tabel untuk 'autogenerate'
from app.models.user import User, Company, Department, Position, WorkStatus
from app.models.vehicle import Vehicle
from app.models.checklist import ChecklistTemplate
from app.models.p2h import P2HReport, P2HDetail, P2HDailyTracker
from app.models.notification import TelegramNotification

# this is the Alembic Config object
config = context.config

# ==================================================================================
# 3. LOGIKA PERBAIKAN URL (FIX ASYNC DRIVER & RAILWAY)
# ==================================================================================
def get_db_url():
    """
    Mengambil URL dari settings dan membersihkannya agar kompatibel dengan Alembic.
    Alembic butuh driver SYNC (psycopg2), bukan ASYNC (asyncpg).
    """
    url = settings.DATABASE_URL
    
    if not url:
        return ""

    # FIX 1: Hapus driver async (+asyncpg) agar menjadi sync standar
    # Mengubah 'postgresql+asyncpg://...' menjadi 'postgresql://...'
    if "postgresql+asyncpg://" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    
    # FIX 2: Handle format legacy Railway/Heroku
    # Mengubah 'postgres://...' menjadi 'postgresql://...'
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    return url

# Set URL database yang sudah diperbaiki ke konfigurasi Alembic
config.set_main_option("sqlalchemy.url", get_db_url())

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Ambil metadata dari Base yang sudah merekam semua model di atas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Ambil URL yang sudah difix oleh fungsi get_db_url() via config
    url = config.get_main_option("sqlalchemy.url")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Ambil section konfigurasi dari file .ini
    configuration = config.get_section(config.config_ini_section) or {}
    
    # PAKSA URL menggunakan yang sudah kita fix (Sync driver)
    # Ini memastikan engine_from_config tidak membaca ulang URL async yang salah
    configuration["sqlalchemy.url"] = get_db_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()