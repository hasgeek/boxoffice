"""add place of supply to item collection and item

Revision ID: f78ca4cad5d6
Revises: 6c04555d7d94
Create Date: 2019-03-22 13:57:06.976453

"""

# revision identifiers, used by Alembic.
revision = 'f78ca4cad5d6'
down_revision = '6c04555d7d94'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('item', sa.Column('place_supply_country_code', sa.Unicode(length=2), nullable=True))
    op.add_column('item', sa.Column('place_supply_state_code', sa.Unicode(length=3), nullable=True))
    op.add_column('item_collection', sa.Column('place_supply_country_code', sa.Unicode(length=2), nullable=True))
    op.add_column('item_collection', sa.Column('place_supply_state_code', sa.Unicode(length=3), nullable=True))
    op.add_column('item', sa.Column('event_date', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('item_collection', 'place_supply_state_code')
    op.drop_column('item_collection', 'place_supply_country_code')
    op.drop_column('item', 'place_supply_state_code')
    op.drop_column('item', 'place_supply_country_code')
    op.drop_column('item', 'event_date')
