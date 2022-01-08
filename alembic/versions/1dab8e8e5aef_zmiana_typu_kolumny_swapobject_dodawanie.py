"""zmiana typu kolumny swapobject dodawanie

Revision ID: 1dab8e8e5aef
Revises: a85196f67c5c
Create Date: 2022-01-08 01:43:40.334663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1dab8e8e5aef'
down_revision = 'a85196f67c5c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'posts',
        sa.Column('swapObject', sa.String(200))
    )



def downgrade():
    pass
