"""add usage limit to discount coupon

Revision ID: 50f34bb47dc4
Revises: 2f6a3bb460b8
Create Date: 2016-04-05 18:46:20.160324

"""

# revision identifiers, used by Alembic.
revision = '50f34bb47dc4'
down_revision = '35952a56c31b'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.sql import table, column


discount_coupon = table('discount_coupon',
  column('used', sa.Boolean()),
  column('usage_limit', sa.Boolean()))

line_item = table('line_item',
  column('discount_coupon_id', sqlalchemy_utils.types.uuid.UUIDType()))


def upgrade():
    op.add_column('discount_coupon', sa.Column('usage_limit', sa.Integer(), nullable=True))
    op.execute(discount_coupon.update().values({'usage_limit': 1}))  # noqa
    op.alter_column('discount_coupon', 'usage_limit',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('discount_coupon', 'used')


def downgrade():
    op.add_column('discount_coupon', sa.Column('used', sa.Boolean(), nullable=False, server_default=False))
    op.execute(discount_coupon.update().where(discount_coupon.c.usage_limit == 1).values({'used': True}))  # noqa
    op.drop_column('discount_coupon', 'usage_limit')
