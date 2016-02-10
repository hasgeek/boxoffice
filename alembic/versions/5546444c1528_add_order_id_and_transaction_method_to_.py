"""add order_id and transaction_method to transaction

Revision ID: 5546444c1528
Revises: 153722fa3bb2
Create Date: 2016-02-10 14:43:01.868086

"""

revision = '5546444c1528'
down_revision = '153722fa3bb2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils

def upgrade():
    op.add_column('transaction', sa.Column('order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True))
    op.add_column('transaction', sa.Column('transaction_method', sa.Integer(), nullable=False))
    op.alter_column('transaction', 'payment_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.create_foreign_key(None, 'transaction', 'order', ['order_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.alter_column('transaction', 'payment_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.drop_column('transaction', 'transaction_method')
    op.drop_column('transaction', 'order_id')
