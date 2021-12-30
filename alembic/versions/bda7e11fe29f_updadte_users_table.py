"""updadte users table

Revision ID: bda7e11fe29f
Revises: 035639beacf6
Create Date: 2021-12-28 20:18:26.335161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bda7e11fe29f'
down_revision = '035639beacf6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('url', sa.String(200)))
    op.add_column('user', sa.Column('address_province', sa.String(200)))
    op.add_column('user', sa.Column('address_city', sa.String(200)))
    op.add_column('user', sa.Column('address_street', sa.String(200)))
    op.add_column('user', sa.Column('address_number', sa.String(200)))


def downgrade():
    pass
