"""added creator_id in comments

Revision ID: d211c1733705
Revises: cd77362aaa2d
Create Date: 2021-12-30 13:54:56.309292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd211c1733705'
down_revision = 'cd77362aaa2d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'comments',
        sa.Column('creator_id', sa.Integer)
    )


def downgrade():
    pass
