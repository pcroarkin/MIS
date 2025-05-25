"""Add last_login and is_active columns to users table

Revision ID: add_user_columns
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add last_login column
    op.add_column('users',
        sa.Column('last_login', sa.DateTime(), nullable=True)
    )
    
    # Add is_active column with default value True
    op.add_column('users',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true())
    )

def downgrade():
    # Remove the columns in reverse order
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_login')
