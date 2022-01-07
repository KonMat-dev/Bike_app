"""added new table Photo

Revision ID: cd77362aaa2d
Revises: bda7e11fe29f
Create Date: 2021-12-28 21:59:23.533993

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cd77362aaa2d'
down_revision = 'bda7e11fe29f'
branch_labels = None
depends_on = None


def upgrade():
    # op.create_table(
    #     'photo',
    #     sa.Column('id', sa.Integer, primary_key=True, unique=True),
    #     sa.Column('post_id', sa.String(200)),
    #     sa.Column('photo_url', sa.String(1000))
    # )
    pass

def downgrade():
    pass
