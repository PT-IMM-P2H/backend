"""add_legacy_vehicle_type_enum_values

Revision ID: c21edccf2f50
Revises: 96b4f334e1df
Create Date: 2026-01-09 08:18:13.920724+08:00

Menambahkan kembali nilai enum legacy (LV, EV, DC, SC, BIS) ke PostgreSQL
untuk backward compatibility agar SQLAlchemy tidak crash saat membaca data lama.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c21edccf2f50'
down_revision = '96b4f334e1df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Menambahkan nilai enum legacy ke PostgreSQL
    # ALTER TYPE ... ADD VALUE ... tidak bisa di-rollback, tapi ini aman
    print("🔄 Menambahkan nilai enum legacy untuk backward compatibility...")
    
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'LV'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'EV'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'DC'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'SC'")
    op.execute("ALTER TYPE vehicletype ADD VALUE IF NOT EXISTS 'BIS'")
    
    print("✅ Nilai enum legacy berhasil ditambahkan:")
    print("   - LV (Light Vehicle)")
    print("   - EV (Electric Vehicle)")
    print("   - DC (Double Cabin)")
    print("   - SC (Single Cabin)")
    print("   - BIS (Bus)")
    print("")
    print("📝 CATATAN:")
    print("   - Enum PostgreSQL sekarang mendukung KEDUA nilai (lama & baru)")
    print("   - Data lama dengan nilai 'LV', 'EV', dll tetap ada (is_active=false)")
    print("   - SQLAlchemy sekarang bisa deserialize data lama tanpa crash")
    print("   - Untuk migrasi data, jalankan migration berikutnya")


def downgrade() -> None:
    # PostgreSQL tidak mendukung DROP VALUE dari enum
    # Alternatif: recreate enum type (terlalu kompleks dan berisiko)
    print("⚠️  Downgrade tidak didukung untuk ALTER TYPE ... ADD VALUE")
    print("   PostgreSQL tidak bisa menghapus nilai dari enum type.")
    print("   Jika perlu rollback, gunakan migration data untuk mengubah nilai.")
    pass
