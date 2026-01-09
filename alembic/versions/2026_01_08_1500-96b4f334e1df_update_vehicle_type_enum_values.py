"""update_vehicle_type_enum_values

Revision ID: 96b4f334e1df
Revises: fb3cd5fa72b9
Create Date: 2026-01-08 15:00:13.920724+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96b4f334e1df'
down_revision = 'fb3cd5fa72b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Soft delete kendaraan lama yang menggunakan enum values yang tidak valid
    # Set is_active = false untuk data dengan enum lama
    op.execute("""
        UPDATE vehicles
        SET is_active = false,
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
    """)
    print("⚠️  Old vehicle data with deprecated enum values has been deactivated.")
    print("    Affected enum values: LV, EV, DC, SC, BIS")
    print("    Please create new vehicle entries with updated enum values:")
    print("    - Light Vehicle")
    print("    - Electric Vehicle")
    print("    - Double Cabin")
    print("    - Single Cabin")
    print("    - Bus")
    print("    - Ambulance")
    print("    - Fire Truck")
    print("    - Komando")
    print("    - Truk Sampah")


def downgrade() -> None:
    # Reactivate the deactivated vehicles
    op.execute("""
        UPDATE vehicles
        SET is_active = true,
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text IN ('LV', 'EV', 'DC', 'SC', 'BIS')
    """)
    print("✅ Reactivated vehicles with old enum values.")
