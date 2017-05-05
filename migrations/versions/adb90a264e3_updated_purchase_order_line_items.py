"""updated purchase order line items

Revision ID: adb90a264e3
Revises: 10ac78260434
Create Date: 2016-04-07 17:36:05.351561

"""

# revision identifiers, used by Alembic.
revision = 'adb90a264e3'
down_revision = '10ac78260434'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import sqlalchemy_utils

order = table('customer_order',
  column('id', sqlalchemy_utils.types.uuid.UUIDType()),
  column('status', sa.Integer))


line_item = table('line_item',
  column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType()),
  column('status', sa.Integer))


def upgrade():
    purchase_order_query = sa.select([order.c.id]).where(order.c.status == 0)
    op.execute(line_item.update().where(line_item.c.customer_order_id.in_(purchase_order_query)).values({'status': 2}))


def downgrade():
    op.execute(line_item.update().where(line_item.c.status == 2).values({'status': 0}))
