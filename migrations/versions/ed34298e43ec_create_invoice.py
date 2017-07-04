"""create_invoice

Revision ID: ed34298e43ec
Revises: 36f458047cfd
Create Date: 2017-07-04 16:10:58.493923

"""

# revision identifiers, used by Alembic.
revision = 'ed34298e43ec'
down_revision = '36f458047cfd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils


def upgrade():
    op.create_table('invoice',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('invoicee_name', sa.Unicode(length=255), nullable=True),
        sa.Column('invoicee_email', sa.Unicode(length=254), nullable=True),
        sa.Column('invoice_no', sa.Unicode(length=32), nullable=True),
        sa.Column('invoiced_at', sa.DateTime(), nullable=True),
        sa.Column('street_address', sa.Unicode(length=255), nullable=True),
        sa.Column('city', sa.Unicode(length=255), nullable=True),
        sa.Column('state', sa.Unicode(length=255), nullable=True),
        sa.Column('country', sa.Unicode(length=255), nullable=True),
        sa.Column('postcode', sa.Unicode(length=8), nullable=True),
        sa.Column('taxid', sa.Unicode(length=255), nullable=True),
        sa.Column('place_of_supply', sa.Unicode(length=3), nullable=True),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'invoice_no')
    )
    op.create_index(op.f('ix_invoice_customer_order_id'), 'invoice', ['customer_order_id'], unique=False)
    op.create_table('invoice_line_item',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('item_title', sa.Unicode(length=255), nullable=False),
        sa.Column('tax_type', sa.Unicode(length=255), nullable=False),
        sa.Column('gst_type', sa.Unicode(length=7), nullable=False),
        sa.Column('discount_title', sa.Unicode(length=255), nullable=False),
        sa.Column('currency', sa.Unicode(length=3), nullable=False),
        sa.Column('base_amount', sa.Numeric(), nullable=False),
        sa.Column('discounted_amount', sa.Numeric(), nullable=False),
        sa.Column('final_amount', sa.Numeric(), nullable=False),
        sa.Column('invoice_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_id', 'seq')
    )
    op.create_index(op.f('ix_invoice_line_item_invoice_id'), 'invoice_line_item', ['invoice_id'], unique=False)
    op.add_column(u'item_collection', sa.Column('tax_type', sa.Unicode(length=80), nullable=True))
    op.add_column(u'item', sa.Column('gst_type', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column(u'item', 'gst_type')
    op.drop_column(u'item_collection', 'tax_type')
    op.drop_index(op.f('ix_invoice_line_item_invoice_id'), table_name='invoice_line_item')
    op.drop_table('invoice_line_item')
    op.drop_index(op.f('ix_invoice_customer_order_id'), table_name='invoice')
    op.drop_table('invoice')
