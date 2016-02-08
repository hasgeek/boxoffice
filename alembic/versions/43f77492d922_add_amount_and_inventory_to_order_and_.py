"""add amount and inventory to order and final_amount to line_item

Revision ID: 43f77492d922
Revises: 3e31bf3b2668
Create Date: 2016-02-08 13:44:12.305606

"""

revision = '43f77492d922'
down_revision = '3e31bf3b2668'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

def upgrade():
    op.add_column('line_item', sa.Column('final_amount', sa.Numeric(), nullable=False))
    op.add_column('order', sa.Column('base_amount', sa.Numeric(), nullable=False))
    op.add_column('order', sa.Column('discounted_amount', sa.Numeric(), nullable=False))
    op.add_column('order', sa.Column('final_amount', sa.Numeric(), nullable=False))
    op.add_column('order', sa.Column('inventory_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False))
    op.create_foreign_key(None, 'order', 'inventory', ['inventory_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'inventory_id')
    op.drop_column('order', 'final_amount')
    op.drop_column('order', 'discounted_amount')
    op.drop_column('order', 'base_amount')
    op.drop_column('line_item', 'final_amount')
