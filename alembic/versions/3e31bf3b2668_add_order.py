"""add order

Revision ID: 3e31bf3b2668
Revises: 19731610c82d
Create Date: 2016-02-07 19:10:39.473133

"""

# revision identifiers, used by Alembic.
revision = '3e31bf3b2668'
down_revision = '19731610c82d'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.create_table('payment',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('pg_payment_id', sa.Unicode(length=80), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('payment_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('amount', sa.Numeric(), nullable=False),
    sa.Column('currency', sa.Unicode(length=3), nullable=False),
    sa.Column('transaction_type', sa.Integer(), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['payment_id'], ['payment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('line_item',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
    sa.Column('item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('base_amount', sa.Numeric(), nullable=False),
    sa.Column('discounted_amount', sa.Numeric(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('line_item')
    op.drop_table('transaction')
    op.drop_table('order')
    op.drop_table('payment')
