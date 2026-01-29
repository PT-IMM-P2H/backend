"""update userrole enum values

Revision ID: 98a0e7fba3a3
Revises: 033b3f0a14d4
Create Date: 2026-01-29 15:41:01.252806+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98a0e7fba3a3'
down_revision = '033b3f0a14d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL ALTER TYPE enum requires special handling
    # Drop and recreate enum with correct values
    
    # First, alter all existing rows to use temporary values
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE VARCHAR(20)
    """)
    
    # Drop old enum type
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
    
    # Create new enum type with lowercase values
    op.execute("""
        CREATE TYPE userrole AS ENUM ('superadmin', 'admin', 'user', 'viewer')
    """)
    
    # Convert column back to enum type
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole USING role::userrole
    """)


def downgrade() -> None:
    # Reverse: convert to VARCHAR, drop new enum, recreate old enum
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE VARCHAR(20)
    """)
    
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
    
    # Recreate old enum (if it had different values)
    op.execute("""
        CREATE TYPE userrole AS ENUM ('superadmin', 'admin', 'user', 'viewer')
    """)
    
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole USING role::userrole
    """)

