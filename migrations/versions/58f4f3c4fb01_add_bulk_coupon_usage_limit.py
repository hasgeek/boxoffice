"""
add_bulk_coupon_usage_limit.

Revision ID: 58f4f3c4fb01
Revises: 48e571c759cb
Create Date: 2016-10-25 17:04:53.487244

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '58f4f3c4fb01'
down_revision = '48e571c759cb'


def upgrade() -> None:
    op.add_column(
        'discount_policy',
        sa.Column('bulk_coupon_usage_limit', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('discount_policy', 'bulk_coupon_usage_limit')
