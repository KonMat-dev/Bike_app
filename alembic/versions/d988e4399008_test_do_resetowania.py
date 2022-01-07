"""test do resetowania

Revision ID: d988e4399008
Revises: 1371a44f0f6d
Create Date: 2022-01-06 23:03:58.195583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd988e4399008'
down_revision = '1371a44f0f6d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'code',
        sa.Column('id', sa.Integer, primary_key=True, unique=True),
        sa.Column('email', sa.String(200), nullable=False, unique=True),
        sa.Column('reset_code', sa.String(200), nullable=False, unique=True),
        sa.Column('status', sa.String(10), nullable=False),
        sa.Column('expired_in', sa.DateTime, nullable=False)
    )




def downgrade():
    pass
