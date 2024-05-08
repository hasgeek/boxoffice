"""
add signed code support.

Revision ID: 510d2db2b008
Revises: 74770336785
Create Date: 2016-07-22 01:28:29.552964

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '510d2db2b008'
down_revision = '74770336785'


def upgrade() -> None:
    # Note: discount_code_base was added in the initial migration (4ffee334e82e),
    # but was removed from the model for a period of time
    op.create_unique_constraint(
        'discount_policy_discount_code_base_key',
        'discount_policy',
        ['discount_code_base'],
    )
    op.add_column(
        'discount_policy', sa.Column('secret', sa.Unicode(length=50), nullable=True)
    )
    op.alter_column(
        'discount_coupon',
        'code',
        existing_type=sa.VARCHAR(length=20),
        type_=sa.VARCHAR(length=100),
    )


def downgrade() -> None:
    op.drop_column('discount_policy', 'secret')
    op.drop_constraint(
        'discount_policy_discount_code_base_key', 'discount_policy', type_='unique'
    )
