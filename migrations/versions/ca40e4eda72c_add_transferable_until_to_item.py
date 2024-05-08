"""
add transferable until to item.

Revision ID: ca40e4eda72c
Revises: cdb214cf1e06
Create Date: 2019-08-01 12:03:12.254758

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ca40e4eda72c'
down_revision = 'cdb214cf1e06'


def upgrade() -> None:
    op.add_column(
        'item',
        sa.Column('transferable_until', sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('item', 'transferable_until')
