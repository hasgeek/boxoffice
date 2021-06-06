"""make is_price_based non nullable.

Revision ID: 35952a56c31b
Revises: 32abb3608d9a
Create Date: 2016-04-04 17:00:42.471535

"""

# revision identifiers, used by Alembic.
revision = '35952a56c31b'
down_revision = '32abb3608d9a'

from alembic import op
from sqlalchemy.sql import column, table
import sqlalchemy as sa

discount_policy = table('discount_policy', column('is_price_based', sa.Boolean()))


def upgrade():
    op.execute(
        discount_policy.update()
        .where(discount_policy.c.is_price_based.is_(None))
        .values({'is_price_based': False})
    )
    op.alter_column(
        'discount_policy', 'is_price_based', existing_type=sa.BOOLEAN(), nullable=False
    )


def downgrade():
    op.alter_column(
        'discount_policy', 'is_price_based', existing_type=sa.BOOLEAN(), nullable=True
    )
    op.execute(
        discount_policy.update()
        .where(discount_policy.c.is_price_based.is_(False))
        .values({'is_price_based': None})
    )
