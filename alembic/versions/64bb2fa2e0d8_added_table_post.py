"""Added table post

Revision ID: 64bb2fa2e0d8
Revises: c372f5434d6c
Create Date: 2021-12-05 21:04:03.321809

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '64bb2fa2e0d8'
down_revision = 'c372f5434d6c'
branch_labels = None
depends_on = None


def upgrade():
    # op.create_table(
    #     'posts',
    #     sa.Column('id', sa.Integer, primary_key=True, unique=True),
    #     sa.Column('title', sa.String(200)),
    #     sa.Column('description', sa.String(500)),
    #     sa.Column('owner_id', sa.Integer),
    #     sa.Column('is_active', sa.Boolean),
    #     sa.Column('created_date', sa.DateTime)
    # )
    pass



def downgrade():
    pass
