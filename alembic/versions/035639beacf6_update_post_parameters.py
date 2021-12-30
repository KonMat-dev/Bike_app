"""Update post parameters

Revision ID: 035639beacf6
Revises: de27993f797b
Create Date: 2021-12-23 15:15:24.165636

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '035639beacf6'
down_revision = 'de27993f797b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('tape_of_service', sa.String(50)))
    op.add_column('posts', sa.Column('address_province', sa.String(100)))
    op.add_column('posts', sa.Column('address_city', sa.String(100)))
    op.add_column('posts', sa.Column('address_street', sa.String(100)))
    op.add_column('posts', sa.Column('address_number', sa.String(40)))
    op.add_column('posts', sa.Column('price', sa.Float(2)))
    op.add_column('posts', sa.Column('category_of_bike', sa.String(200)))


def downgrade():
    pass
