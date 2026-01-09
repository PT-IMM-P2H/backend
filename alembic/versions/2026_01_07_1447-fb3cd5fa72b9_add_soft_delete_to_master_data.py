"""add_soft_delete_to_master_data

Revision ID: fb3cd5fa72b9
Revises: 4a3f44d85540
Create Date: 2026-01-07 14:47:36.912216+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb3cd5fa72b9'
down_revision = '4a3f44d85540'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_active and deleted_at columns to companies table
    op.add_column('companies', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('companies', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_companies_is_active', 'companies', ['is_active'])
    
    # Add is_active and deleted_at columns to departments table
    op.add_column('departments', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('departments', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_departments_is_active', 'departments', ['is_active'])
    
    # Add is_active and deleted_at columns to positions table
    op.add_column('positions', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('positions', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_positions_is_active', 'positions', ['is_active'])
    
    # Add is_active and deleted_at columns to work_statuses table
    op.add_column('work_statuses', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('work_statuses', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_work_statuses_is_active', 'work_statuses', ['is_active'])


def downgrade() -> None:
    # Drop indexes and columns for work_statuses
    op.drop_index('ix_work_statuses_is_active', table_name='work_statuses')
    op.drop_column('work_statuses', 'deleted_at')
    op.drop_column('work_statuses', 'is_active')
    
    # Drop indexes and columns for positions
    op.drop_index('ix_positions_is_active', table_name='positions')
    op.drop_column('positions', 'deleted_at')
    op.drop_column('positions', 'is_active')
    
    # Drop indexes and columns for departments
    op.drop_index('ix_departments_is_active', table_name='departments')
    op.drop_column('departments', 'deleted_at')
    op.drop_column('departments', 'is_active')
    
    # Drop indexes and columns for companies
    op.drop_index('ix_companies_is_active', table_name='companies')
    op.drop_column('companies', 'deleted_at')
    op.drop_column('companies', 'is_active')
