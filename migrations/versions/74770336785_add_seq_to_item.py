"""
add seq to item.

Revision ID: 74770336785
Revises: 59d274a1682f
Create Date: 2016-07-06 10:09:49.553138

"""

# revision identifiers, used by Alembic.
revision = '74770336785'
down_revision = '59d274a1682f'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

item_collection = table('item_collection', column('id', postgresql.UUID()))

item = table(
    'item',
    column('id', postgresql.UUID()),
    column('item_collection_id', postgresql.UUID()),
    column('seq', sa.Integer()),
    column('created_at', sa.DateTime()),
)


def upgrade() -> None:
    op.add_column('item', sa.Column('seq', sa.Integer(), nullable=True))
    connection = op.get_bind()
    item_collections = connection.execute(sa.select(item_collection.c.id))
    item_collection_ids = [ic_tuple[0] for ic_tuple in item_collections]
    for item_collection_id in item_collection_ids:
        items = connection.execute(
            sa.select(item.c.id)
            .where(item.c.item_collection_id == item_collection_id)
            .order_by(sa.text('created_at'))
        )
        item_ids = [item_tuple[0] for item_tuple in items]
        for idx, item_id in enumerate(item_ids):
            op.execute(
                item.update().where(item.c.id == item_id).values({'seq': idx + 1})
            )
    op.alter_column('item', 'seq', existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    op.drop_column('item', 'seq')
