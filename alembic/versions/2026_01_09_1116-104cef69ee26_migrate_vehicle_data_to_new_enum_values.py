"""migrate_vehicle_data_to_new_enum_values

Revision ID: 104cef69ee26
Revises: 1ad8653c1175
Create Date: 2026-01-09 11:16:42.434617+08:00

Mengupdate data kendaraan dari nilai enum lama (LV, EV, DC, BIS, SC)
ke nilai enum baru (Light Vehicle, Electric Vehicle, dll)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '104cef69ee26'
down_revision = '1ad8653c1175'
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("🔄 Mengupdate data kendaraan ke nilai enum baru...")
    
    # Update vehicle records dari nilai lama ke nilai baru
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'Light Vehicle',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'LV'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'Electric Vehicle',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'EV'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'Double Cabin',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'DC'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'Single Cabin',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'SC'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'Bus',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'BIS'
    """)
    
    print("✅ Data kendaraan berhasil diupdate:")
    print("   - LV → Light Vehicle")
    print("   - EV → Electric Vehicle")
    print("   - DC → Double Cabin")
    print("   - SC → Single Cabin")
    print("   - BIS → Bus")


def downgrade() -> None:
    print("🔄 Mengembalikan data kendaraan ke nilai enum lama...")
    
    # Rollback vehicle records ke nilai lama
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'LV',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'Light Vehicle'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'EV',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'Electric Vehicle'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'DC',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'Double Cabin'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'SC',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'Single Cabin'
    """)
    
    op.execute("""
        UPDATE vehicles
        SET vehicle_type = 'BIS',
            updated_at = CURRENT_TIMESTAMP
        WHERE vehicle_type::text = 'Bus'
    """)
    
    print("✅ Data kendaraan dikembalikan ke nilai enum lama")
