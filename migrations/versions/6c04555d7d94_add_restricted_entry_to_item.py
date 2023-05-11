"""add_restricted_entry_to_item.

Revision ID: 6c04555d7d94
Revises: 829f42c03de3
Create Date: 2018-04-24 15:59:45.233516

"""

from alembic import op
from sqlalchemy.sql import column, table
import sqlalchemy as sa

revision = '6c04555d7d94'
down_revision = '829f42c03de3'


def upgrade():
    item_table = table('item', column('restricted_entry', sa.Boolean()))

    op.add_column('item', sa.Column('restricted_entry', sa.Boolean(), nullable=True))
    op.execute(item_table.update().values({'restricted_entry': False}))
    op.alter_column(
        'item', 'restricted_entry', existing_type=sa.Boolean(), nullable=False
    )


def downgrade():
    op.drop_column('item', 'restricted_entry')
