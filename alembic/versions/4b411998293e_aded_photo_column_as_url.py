"""aded photo column as url

Revision ID: 4b411998293e
Revises: 64bb2fa2e0d8
Create Date: 2021-12-06 23:25:42.467610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b411998293e'
down_revision = '64bb2fa2e0d8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'posts',
        sa.Column('url', sa.String(200))
    )
    pass


def downgrade():
    pass
