"""add_seq_to_item

Revision ID: 489b96aed483
Revises: 4d7f840202d2
Create Date: 2016-03-30 13:15:27.012266

"""

# revision identifiers, used by Alembic.
revision = '489b96aed483'
down_revision = '4d7f840202d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('item', sa.Column('seq', sa.Integer(), nullable=False))
    op.create_unique_constraint('item_seq_key', 'item', ['category_id', 'seq'])


def downgrade():
    op.drop_constraint('item_seq_key', 'item', type_='unique')
    op.drop_column('item', 'seq')
