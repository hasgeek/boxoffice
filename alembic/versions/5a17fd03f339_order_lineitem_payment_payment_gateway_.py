import sqlalchemy_utils
from coaster.sqlalchemy import JsonDict
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

"""order lineitem payment payment gateway transaction

Revision ID: 5a17fd03f339
Revises: 193d0f40c6
Create Date: 2016-02-01 16:43:22.303867

"""

# revision identifiers, used by Alembic.
revision = '5a17fd03f339'
down_revision = '193d0f40c6'


def upgrade():
    op.create_table('payment_gateway',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('data', JsonDict(), server_default='{}', nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('order',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('payment',
        sa.Column('payment_gateway_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column('pg_payment_id', sa.Unicode(length=80), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['payment_gateway_id'], ['payment_gateway.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction',
        sa.Column('order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('transaction_type', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.ForeignKeyConstraint(['payment_id'], ['payment.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('line_item',
        sa.Column('order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column('item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('base_amount', sa.Float(), nullable=False),
        sa.Column('discounted_amount', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('customer')


def downgrade():
    op.create_table('customer',
        sa.Column('fullname', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(length=254), autoincrement=False, nullable=False),
        sa.Column('phone', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
        sa.Column('email_verified', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('address', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
        sa.Column('account_id', postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['account_id'], [u'customer.id'], name=u'customer_account_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'customer_pkey')
    )
    op.drop_table('line_item')
    op.drop_table('transaction')
    op.drop_table('payment')
    op.drop_table('order')
    op.drop_table('payment_gateway')
