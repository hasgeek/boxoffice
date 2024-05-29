"""
add usage limit to discount coupon.

Revision ID: 50f34bb47dc4
Revises: 2f6a3bb460b8
Create Date: 2016-04-05 18:46:20.160324

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '50f34bb47dc4'
down_revision = '35952a56c31b'


discount_coupon = table(
    'discount_coupon',
    column('id', postgresql.UUID()),
    column('used', sa.Boolean()),
    column('used_count', sa.Integer()),
    column('usage_limit', sa.Integer()),
)

line_item = table(
    'line_item',
    column('discount_coupon_id', postgresql.UUID()),
)


def upgrade() -> None:
    op.add_column(
        'discount_coupon',
        sa.Column('usage_limit', sa.Integer(), nullable=False, server_default='1'),
    )
    op.add_column(
        'discount_coupon',
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.execute(
        discount_coupon.update()
        .where(line_item.c.discount_coupon_id == discount_coupon.c.id)
        .values({'used_count': 1})
    )
    op.alter_column('discount_coupon', 'usage_limit', server_default=None)
    op.alter_column('discount_coupon', 'used_count', server_default=None)
    op.drop_column('discount_coupon', 'used')


def downgrade() -> None:
    op.add_column(
        'discount_coupon',
        sa.Column('used', sa.Boolean(), nullable=False, server_default='0'),
    )
    op.execute(
        discount_coupon.update()
        .where(line_item.c.discount_coupon_id == discount_coupon.c.id)
        .values({'used': True})
    )
    op.alter_column('discount_coupon', 'used', server_default=None)
    op.drop_column('discount_coupon', 'usage_limit')
    op.drop_column('discount_coupon', 'used_count')
