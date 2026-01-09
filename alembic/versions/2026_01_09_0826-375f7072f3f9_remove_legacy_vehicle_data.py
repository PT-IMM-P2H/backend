"""remove_legacy_vehicle_data

Revision ID: 375f7072f3f9
Revises: c21edccf2f50
Create Date: 2026-01-09 08:26:13.920724+08:00

Menghapus (hard delete) data kendaraan lama dengan nilai enum legacy.
Data ini sudah di-soft delete sebelumnya dan tidak digunakan lagi.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '375f7072f3f9'
down_revision = 'c21edccf2f50'
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("🗑️  Menghapus data kendaraan legacy (hard delete)...")
    
    # Hapus data dari tabel yang reference vehicles (foreign keys)
    # Urutan penting: hapus child records dulu sebelum parent
    op.execute("""
        DELETE FROM p2h_daily_tracker 
        WHERE vehicle_id IN (
            SELECT id FROM vehicles 
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
        )
    """)
    
    op.execute("""
        DELETE FROM p2h_reports 
        WHERE vehicle_id IN (
            SELECT id FROM vehicles 
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
        )
    """)
    
    op.execute("""
        DELETE FROM telegram_notifications 
        WHERE vehicle_id IN (
            SELECT id FROM vehicles 
            WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
        )
    """)
    
    # Terakhir, hapus vehicles itu sendiri
    result = op.execute("""
        DELETE FROM vehicles 
        WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
    """)
    
    print("✅ Data kendaraan legacy berhasil dihapus dari database")
    print("")
    print("📝 CATATAN:")
    print("   - Data kendaraan dengan nilai LV, EV, DC, SC, BIS sudah dihapus permanen")
    print("   - Enum PostgreSQL masih memiliki nilai legacy (aman, tidak berbahaya)")
    print("   - Python model akan diupdate untuk hanya expose nilai baru")


def downgrade() -> None:
    print("⚠️  Downgrade tidak tersedia - data sudah dihapus permanen")
    print("   Jika perlu restore, gunakan backup database")
    pass
