"""test

Revision ID: de27993f797b
Revises: 4b411998293e
Create Date: 2021-12-22 12:32:55.650561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de27993f797b'
down_revision = '4b411998293e'
branch_labels = None
depends_on = None


def upgrade():
    # op.add_column(
    #     'comments',
    #     sa.Column('id', sa.Integer, primary_key=True, unique=True),
    #     sa.Column('name', sa.String(100)),
    #     sa.Column('email', sa.String(100)),
    #     sa.Column('description', sa.String(1000)),
    #     sa.Column('owner_id', sa.Integer),
    #     sa.Column('is_active', sa.Boolean),
    #     sa.Column('mark', sa.Integer),
    #     sa.Column('created_date', sa.DateTime)
    # )
    pass

def downgrade():
    pass
