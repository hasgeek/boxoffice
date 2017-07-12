"""add details to item itemcollection

Revision ID: 3d55fce529de
Revises: 36f458047cfd
Create Date: 2017-05-31 15:31:09.140120

"""

# revision identifiers, used by Alembic.
revision = '3d55fce529de'
down_revision = '36f458047cfd'

from alembic import op
import sqlalchemy as sa
from coaster import sqlalchemy


def upgrade():
    op.add_column('item', sa.Column('details', sqlalchemy.JsonDict(), nullable=False, server_default='{}'))
    op.add_column('item_collection', sa.Column('details', sqlalchemy.JsonDict(), nullable=False, server_default='{}'))


def downgrade():
    op.drop_column('item_collection', 'details')
    op.drop_column('item', 'details')
