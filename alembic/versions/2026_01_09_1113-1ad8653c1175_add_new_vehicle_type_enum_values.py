"""add_new_vehicle_type_enum_values

Revision ID: 1ad8653c1175
Revises: 375f7072f3f9
Create Date: 2026-01-09 11:13:30.932001+08:00

Menambahkan nilai enum baru ke PostgreSQL untuk VehicleType
(Light Vehicle, Electric Vehicle, dll)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ad8653c1175'
down_revision = '375f7072f3f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("🔄 Menambahkan nilai enum baru untuk VehicleType...")
    
    # Menambahkan nilai enum baru ke PostgreSQL
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Light Vehicle'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Electric Vehicle'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Double Cabin'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Single Cabin'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Bus'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Ambulance'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Fire Truck'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Komando'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'Truk Sampah'")
    
    print("✅ Nilai enum baru berhasil ditambahkan:")
    print("   - Light Vehicle")
    print("   - Electric Vehicle")
    print("   - Double Cabin")
    print("   - Single Cabin")
    print("   - Bus")
    print("   - Ambulance")
    print("   - Fire Truck")
    print("   - Komando")
    print("   - Truk Sampah")


def downgrade() -> None:
    # PostgreSQL tidak mendukung DROP VALUE dari enum
    print("⚠️  Downgrade tidak didukung untuk ALTER TYPE ... ADD VALUE")
    pass

