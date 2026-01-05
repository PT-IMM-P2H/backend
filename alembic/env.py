from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
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

# 3. Set URL database dari file konfigurasi aplikasi kita (.env via settings)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Ambil metadata dari Base yang sudah merekam semua model di atas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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