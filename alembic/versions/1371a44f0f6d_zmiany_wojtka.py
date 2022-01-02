"""Zmiany wojtka

Revision ID: 1371a44f0f6d
Revises: d211c1733705
Create Date: 2022-01-02 19:36:25.488917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1371a44f0f6d'
down_revision = 'd211c1733705'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('swapObject', sa.Boolean))
    op.add_column('posts', sa.Column('rentalPeriod', sa.Float(2)))

    op.add_column('user', sa.Column('firstName', sa.String(100)))
    op.add_column('user', sa.Column('lastName', sa.String(100)))
    op.add_column('user', sa.Column('phone', sa.String(100)))



def downgrade():
    pass
