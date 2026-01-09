"""update user table columns to email and phone_number

Revision ID: 4a3f44d85540
Revises: 615b363ece3a
Create Date: 2026-01-07 09:55:58.809480+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a3f44d85540'
down_revision = '615b363ece3a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename no_handphone to phone_number
    op.alter_column('users', 'no_handphone', new_column_name='phone_number')
    
    # Add email column (nullable first to allow existing data)
    op.add_column('users', sa.Column('email', sa.String(100), nullable=True))
    
    # Create index on email
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Drop username and first_name columns
    op.drop_column('users', 'username')
    op.drop_column('users', 'first_name')


def downgrade() -> None:
    # Add back username and first_name
    op.add_column('users', sa.Column('username', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(50), nullable=True))
    
    # Drop email column and its index
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'email')
    
    # Rename phone_number back to no_handphone
    op.alter_column('users', 'phone_number', new_column_name='no_handphone')
