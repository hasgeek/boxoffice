from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import coaster

"""init models

Revision ID: 4ffee334e82e
Revises: None
Create Date: 2016-02-25 16:35:04.042785

"""

revision = '4ffee334e82e'
down_revision = None


def upgrade():
    op.create_table('organization',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('userid', sa.Unicode(length=22), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('userid')
    )
    op.create_table('user',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('lastuser_token_scope', sa.Unicode(length=250), nullable=True),
        sa.Column('lastuser_token_type', sa.Unicode(length=250), nullable=True),
        sa.Column('userinfo', coaster.sqlalchemy.JsonDict(), nullable=True),
        sa.Column('email', sa.Unicode(length=80), nullable=True),
        sa.Column('lastuser_token', sa.String(length=22), nullable=True),
        sa.Column('username', sa.Unicode(length=80), nullable=True),
        sa.Column('userid', sa.String(length=22), nullable=False),
        sa.Column('fullname', sa.Unicode(length=80), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('lastuser_token'),
        sa.UniqueConstraint('userid'),
        sa.UniqueConstraint('username')
    )
    op.create_table('discount_policy',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('discount_type', sa.Integer(), nullable=False),
        sa.Column('item_quantity_min', sa.Integer(), nullable=False),
        sa.Column('item_quantity_max', sa.Integer(), nullable=True),
        sa.Column('discount_code_base', sa.Unicode(length=20), nullable=True),
        sa.Column('percentage', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.CheckConstraint(u'item_quantity_min <= item_quantity_max', name='discount_policy_item_quantity_check'),
        sa.CheckConstraint(u'percentage > 0 and percentage <= 100', name='discount_policy_percentage_check'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name')
    )
    op.create_table('item_collection',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('description', sa.Unicode(length=2500), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name')
    )
    op.create_table('category',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['item_collection_id'], ['item_collection.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_collection_id', 'name')
    )
    op.create_table('customer_order',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('initiated_at', sa.DateTime(), nullable=False),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('invoiced_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('access_token', sa.Unicode(length=22), nullable=False),
        sa.Column('buyer_email', sa.Unicode(length=254), nullable=False),
        sa.Column('buyer_fullname', sa.Unicode(length=80), nullable=False),
        sa.Column('buyer_phone', sa.Unicode(length=16), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('invoice_no', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['item_collection_id'], ['item_collection.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'invoice_no')
    )
    op.create_table('discount_coupon',
        sa.Column('code', sa.Unicode(length=20), nullable=False),
        sa.Column('discount_policy_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('quantity_available', sa.Integer(), nullable=False),
        sa.Column('quantity_total', sa.Integer(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.CheckConstraint(u'quantity_available <= quantity_total', name='discount_coupon_quantity_check'),
        sa.ForeignKeyConstraint(['discount_policy_id'], ['discount_policy.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discount_policy_id', 'code')
    )
    op.create_table('item',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('description', sa.Unicode(length=2500), nullable=False),
        sa.Column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('quantity_available', sa.Integer(), nullable=False),
        sa.Column('quantity_total', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
        sa.ForeignKeyConstraint(['item_collection_id'], ['item_collection.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_collection_id', 'name'),
        sa.CheckConstraint(u'quantity_available <= quantity_total', name='item_quantity_available_lte_quantity_total_check')
    )
    op.create_table('online_payment',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('pg_payment_id', sa.Unicode(length=80), nullable=False),
        sa.Column('pg_payment_status', sa.Integer(), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_discount_policy',
        sa.Column('item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('discount_policy_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['discount_policy_id'], ['discount_policy.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.PrimaryKeyConstraint('item_id', 'discount_policy_id')
    )
    op.create_table('line_item',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('discount_policy_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column('discount_coupon_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column('base_amount', sa.Numeric(), nullable=False),
        sa.Column('discounted_amount', sa.Numeric(), nullable=False),
        sa.Column('final_amount', sa.Numeric(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('ordered_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('line_item_no', sa.Integer(), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.ForeignKeyConstraint(['discount_policy_id'], ['discount_policy.id'], ),
        sa.ForeignKeyConstraint(['discount_coupon_id'], ['discount_coupon.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.UniqueConstraint('customer_order_id', 'line_item_no'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment_transaction',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('online_payment_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('currency', sa.Unicode(length=3), nullable=False),
        sa.Column('transaction_type', sa.Integer(), nullable=False),
        sa.Column('transaction_method', sa.Integer(), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.ForeignKeyConstraint(['online_payment_id'], ['online_payment.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('price',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_upto', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('currency', sa.Unicode(length=3), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('price')
    op.drop_table('line_item')
    op.drop_table('item_discount_policy')
    op.drop_table('payment_transaction')
    op.drop_table('online_payment')
    op.drop_table('item')
    op.drop_table('discount_coupon')
    op.drop_table('customer_order')
    op.drop_table('category')
    op.drop_table('item_collection')
    op.drop_table('discount_policy')
    op.drop_table('user')
    op.drop_table('organization')
