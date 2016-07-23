"""add signed code support

Revision ID: 510d2db2b008
Revises: 74770336785
Create Date: 2016-07-22 01:28:29.552964

"""

# revision identifiers, used by Alembic.
revision = '510d2db2b008'
down_revision = '74770336785'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('discount_policy', 'discount_code_base')
    op.add_column('discount_policy', sa.Column('discount_code_base', sa.Unicode(length=50), nullable=True))
    op.create_unique_constraint('discount_policy_discount_code_base_key', 'discount_policy', ['discount_code_base'])
    op.add_column('discount_policy', sa.Column('secret', sa.Unicode(length=50), nullable=True))

    op.alter_column('discount_coupon', 'code', existing_type=sa.VARCHAR(length=20), type_=sa.VARCHAR(length=100))


def downgrade():
    op.drop_column('discount_policy', 'secret')
    op.drop_constraint('discount_policy_discount_code_base_key', 'discount_policy', type_='unique')
    op.drop_column('discount_policy', 'discount_code_base')
    op.add_column('discount_policy', sa.Column('discount_code_base', sa.Unicode(length=20), nullable=True))
