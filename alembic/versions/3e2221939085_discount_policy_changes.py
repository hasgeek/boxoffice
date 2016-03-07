"""discount_policy_changes

Revision ID: 3e2221939085
Revises: 4ffee334e82e
Create Date: 2016-03-02 09:30:03.871802

"""

revision = '3e2221939085'
down_revision = '4ffee334e82e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('discount_coupon', sa.Column('used_at', sa.DateTime(), nullable=True))
    op.drop_column('discount_coupon', 'quantity_available')
    op.drop_column('discount_coupon', 'quantity_total')
    op.add_column('discount_policy', sa.Column('discount_code_base', sa.Unicode(length=20), nullable=True))


def downgrade():
    op.drop_column('discount_policy', 'discount_code_base')
    op.add_column('discount_coupon', sa.Column('quantity_total', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('discount_coupon', sa.Column('quantity_available', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('discount_coupon', 'used_at')
