"""add seq to item

Revision ID: 74770336785
Revises: 59d274a1682f
Create Date: 2016-07-06 10:09:49.553138

"""

# revision identifiers, used by Alembic.
revision = '74770336785'
down_revision = '59d274a1682f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import sqlalchemy_utils

item_collection = table('item_collection', column('id', sqlalchemy_utils.types.uuid.UUIDType()))

item = table('item',
    column('id', sqlalchemy_utils.types.uuid.UUIDType()),
    column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType()),
    column('seq', sa.Integer()),
    column('created_at', sa.DateTime()))


def upgrade():
    op.add_column('item', sa.Column('seq', sa.Integer(), nullable=True))
    connection = op.get_bind()
    item_collections = connection.execute(sa.select([item_collection.c.id]))
    item_collection_ids = [ic_tuple[0] for ic_tuple in item_collections]
    for item_collection_id in item_collection_ids:
        items = connection.execute(sa.select([item.c.id]).where(item.c.item_collection_id == item_collection_id).order_by('created_at'))
        item_ids = [item_tuple[0] for item_tuple in items]
        for idx, item_id in enumerate(item_ids):
            op.execute(item.update().where(item.c.id == item_id).values({'seq': idx + 1}))
    op.alter_column('item', 'seq', existing_type=sa.Integer(), nullable=False)


def downgrade():
    op.drop_column('item', 'seq')
