"""
add discount_policy_id to price.

Revision ID: 45de268cd444
Revises: 4d7f840202d2
Create Date: 2016-03-31 15:29:51.897720

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '45de268cd444'
down_revision = '4d7f840202d2'


def upgrade() -> None:
    op.add_column(
        'price',
        sa.Column('discount_policy_id', postgresql.UUID(), nullable=True),
    )
    op.create_unique_constraint(
        'price_item_id_discount_policy_id_key',
        'price',
        ['item_id', 'discount_policy_id'],
    )
    op.create_foreign_key(
        'price_discount_policy_id_fkey',
        'price',
        'discount_policy',
        ['discount_policy_id'],
        ['id'],
    )
    op.alter_column(
        'discount_policy', 'percentage', existing_type=sa.INTEGER, nullable=True
    )
    op.add_column(
        'discount_policy', sa.Column('is_price_based', sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    op.drop_constraint('price_discount_policy_id_fkey', 'price', type_='foreignkey')
    op.drop_constraint('price_item_id_discount_policy_id_key', 'price', type_='unique')
    op.drop_column('price', 'discount_policy_id')
    op.drop_column('discount_policy', 'is_price_based')
    op.alter_column(
        'discount_policy', 'percentage', existing_type=sa.INTEGER, nullable=False
    )
