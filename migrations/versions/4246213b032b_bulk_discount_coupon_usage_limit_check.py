"""bulk_discount_coupon_usage_limit_check.

Revision ID: 4246213b032b
Revises: 58f4f3c4fb01
Create Date: 2016-10-27 04:07:21.617514

"""

from alembic import op
from sqlalchemy.sql import column, table
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4246213b032b'
down_revision = '58f4f3c4fb01'


discount_policy = table(
    'discount_policy',
    column('discount_type', sa.Integer()),
    column('bulk_coupon_usage_limit', sa.Integer()),
)


def upgrade():
    op.execute(
        discount_policy.update()
        .where(discount_policy.c.discount_type == 1)
        .where(discount_policy.c.bulk_coupon_usage_limit.is_(None))
        .values({'bulk_coupon_usage_limit': 1})
    )
    op.create_check_constraint(
        'discount_policy_bulk_coupon_usage_limit_check',
        'discount_policy',
        'discount_type = 0 or (discount_type = 1 and bulk_coupon_usage_limit IS NOT NULL)',
    )


def downgrade():
    op.drop_constraint(
        'discount_policy_bulk_coupon_usage_limit_check', 'discount_policy'
    )
