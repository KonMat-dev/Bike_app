"""zmiana typu kolumny swapobject usuwanie 

Revision ID: a85196f67c5c
Revises: d988e4399008
Create Date: 2022-01-08 01:40:03.034438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a85196f67c5c'
down_revision = 'd988e4399008'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('swapObject')
    pass
def downgrade():
    pass
