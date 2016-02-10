"""rm amounts from order

Revision ID: 4a7b87015bcb
Revises: 5546444c1528
Create Date: 2016-02-10 19:16:25.084252

"""

revision = '4a7b87015bcb'
down_revision = '5546444c1528'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('order', 'discounted_amount')
    op.drop_column('order', 'base_amount')
    op.drop_column('order', 'final_amount')


def downgrade():
    op.add_column('order', sa.Column('final_amount', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.add_column('order', sa.Column('base_amount', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.add_column('order', sa.Column('discounted_amount', sa.NUMERIC(), autoincrement=False, nullable=False))
