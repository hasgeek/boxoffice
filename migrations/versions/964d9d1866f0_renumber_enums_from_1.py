"""
Renumber enums from 1.

Revision ID: 964d9d1866f0
Revises: 50b7f36bb7eb
Create Date: 2024-05-28 19:14:32.583933

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '964d9d1866f0'
down_revision: str = '50b7f36bb7eb'


discount_policy = sa.table(
    'discount_policy',
    sa.column('discount_type', sa.Integer()),
    sa.column('bulk_coupon_usage_limit', sa.Integer()),
)
invoice = sa.table('invoice', sa.column('status', sa.SmallInteger()))
line_item = sa.table('line_item', sa.column('status', sa.Integer()))
customer_order = sa.table('customer_order', sa.column('status', sa.Integer()))
payment_transaction = sa.table(
    'payment_transaction',
    sa.column('transaction_method', sa.Integer()),
    sa.column('transaction_type', sa.Integer()),
)


def upgrade() -> None:
    op.alter_column(
        'invoice',
        'invoiced_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.drop_constraint(
        'discount_policy_bulk_coupon_usage_limit_check',
        'discount_policy',
        type_='check',
    )
    op.execute(
        discount_policy.update().values(
            discount_type=discount_policy.c.discount_type + 1
        )
    )
    op.execute(invoice.update().values(status=invoice.c.status + 1))
    op.execute(line_item.update().values(status=line_item.c.status + 1))
    op.execute(customer_order.update().values(status=customer_order.c.status + 1))
    op.execute(
        payment_transaction.update().values(
            transaction_method=payment_transaction.c.transaction_method + 1,
            transaction_type=payment_transaction.c.transaction_type + 1,
        )
    )
    op.create_check_constraint(
        'discount_policy_bulk_coupon_usage_limit_check',
        'discount_policy',
        sa.or_(
            discount_policy.c.discount_type == 1,
            sa.and_(
                discount_policy.c.discount_type == 2,
                discount_policy.c.bulk_coupon_usage_limit.isnot(None),
            ),
        ),
    )


def downgrade() -> None:
    op.drop_constraint(
        'discount_policy_bulk_coupon_usage_limit_check',
        'discount_policy',
        type_='check',
    )
    op.execute(
        payment_transaction.update().values(
            transaction_method=payment_transaction.c.transaction_method - 1,
            transaction_type=payment_transaction.c.transaction_type - 1,
        )
    )
    op.execute(customer_order.update().values(status=customer_order.c.status - 1))
    op.execute(line_item.update().values(status=line_item.c.status - 1))
    op.execute(invoice.update().values(status=invoice.c.status - 1))
    op.execute(
        discount_policy.update().values(
            discount_type=discount_policy.c.discount_type - 1
        )
    )
    op.alter_column(
        'invoice',
        'invoiced_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.create_check_constraint(
        'discount_policy_bulk_coupon_usage_limit_check',
        'discount_policy',
        sa.or_(
            discount_policy.c.discount_type == 0,
            sa.and_(
                discount_policy.c.discount_type == 1,
                discount_policy.c.bulk_coupon_usage_limit.isnot(None),
            ),
        ),
    )
