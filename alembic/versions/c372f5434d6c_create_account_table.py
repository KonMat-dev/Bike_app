"""create account table

Revision ID: c372f5434d6c
Revises: 
Create Date: 2021-11-30 13:27:18.989181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c372f5434d6c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, unique=True),
        sa.Column('username', sa.String(200), nullable=False, unique=True),
        sa.Column('email', sa.String(200), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('created_date', sa.DateTime, nullable=False),
        sa.Column('description', sa.String(500)),
    )


def downgrade():
    pass
