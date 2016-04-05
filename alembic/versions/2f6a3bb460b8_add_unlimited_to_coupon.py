"""add unlimited to coupon

Revision ID: 2f6a3bb460b8
Revises: 35952a56c31b
Create Date: 2016-04-05 13:30:41.724690

"""

# revision identifiers, used by Alembic.
revision = '2f6a3bb460b8'
down_revision = '35952a56c31b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade():
    discount_coupon = table('discount_coupon',
      column('unlimited', sa.Boolean()))
    op.add_column('discount_coupon', sa.Column('unlimited', sa.Boolean(), nullable=True))
    op.execute(discount_coupon.update().values({'unlimited': False}))
    op.alter_column('discount_coupon', 'unlimited',
               existing_type=sa.BOOLEAN(),
               nullable=False)


def downgrade():
    op.drop_column('discount_coupon', 'unlimited')
