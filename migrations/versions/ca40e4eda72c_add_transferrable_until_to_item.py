"""add transferrable until to item

Revision ID: ca40e4eda72c
Revises: cdb214cf1e06
Create Date: 2019-08-01 12:03:12.254758

"""

# revision identifiers, used by Alembic.
revision = 'ca40e4eda72c'
down_revision = 'cdb214cf1e06'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('item', sa.Column('transferrable_until', sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade():
    op.drop_column('item', 'transferrable_until')
