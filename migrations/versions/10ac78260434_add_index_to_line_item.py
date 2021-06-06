"""add index to line_item.

Revision ID: 10ac78260434
Revises: 50f34bb47dc4
Create Date: 2016-04-06 21:56:46.837105

"""

# revision identifiers, used by Alembic.
revision = '10ac78260434'
down_revision = '50f34bb47dc4'

from alembic import op


def upgrade():
    op.create_index(
        op.f('ix_line_item_customer_order_id'),
        'line_item',
        ['customer_order_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_line_item_item_id'), 'line_item', ['item_id'], unique=False
    )
    op.create_index(
        op.f('ix_line_item_discount_policy_id'),
        'line_item',
        ['discount_policy_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_line_item_discount_coupon_id'),
        'line_item',
        ['discount_coupon_id'],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f('ix_line_item_customer_order_id'), table_name='line_item')
    op.drop_index(op.f('ix_line_item_item_id'), table_name='line_item')
    op.drop_index(op.f('ix_line_item_discount_policy_id'), table_name='line_item')
    op.drop_index(op.f('ix_line_item_discount_coupon_id'), table_name='line_item')
