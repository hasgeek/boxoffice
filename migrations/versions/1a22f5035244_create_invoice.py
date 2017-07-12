"""create_invoice

Revision ID: 1a22f5035244
Revises: 36f458047cfd
Create Date: 2017-07-05 15:32:02.514565

"""

# revision identifiers, used by Alembic.
revision = '1a22f5035244'
down_revision = '36f458047cfd'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('invoice',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('invoicee_name', sa.Unicode(length=255), nullable=True),
        sa.Column('invoicee_email', sa.Unicode(length=254), nullable=True),
        sa.Column('invoice_no', sa.Integer(), nullable=True),
        sa.Column('invoiced_at', sa.DateTime(), nullable=True),
        sa.Column('street_address', sa.Unicode(length=255), nullable=True),
        sa.Column('city', sa.Unicode(length=255), nullable=True),
        sa.Column('state', sa.Unicode(length=255), nullable=True),
        sa.Column('state_code', sa.Unicode(length=4), nullable=True),
        sa.Column('country_code', sa.Unicode(length=2), nullable=True),
        sa.Column('postcode', sa.Unicode(length=8), nullable=True),
        sa.Column('buyer_taxid', sa.Unicode(length=255), nullable=True),
        sa.Column('seller_taxid', sa.Unicode(length=255), nullable=True),
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
        sa.Column('quantity', sa.SmallInteger(), nullable=False),
        sa.Column('tax_type', sa.Unicode(length=255), nullable=False),
        sa.Column('gst_type', sa.Unicode(length=7), nullable=False),
        sa.Column('discount_title', sa.Unicode(length=255), nullable=False),
        sa.Column('currency', sa.Unicode(length=3), nullable=False),
        sa.Column('base_amount', sa.Numeric(), nullable=False),
        sa.Column('discounted_amount', sa.Numeric(), nullable=False),
        sa.Column('total_amount', sa.Numeric(), nullable=False),
        sa.Column('cgst_tax_rate', sa.Integer(), nullable=True),
        sa.Column('sgst_tax_rate', sa.Integer(), nullable=True),
        sa.Column('igst_tax_rate', sa.Integer(), nullable=True),
        sa.Column('gst_compensation_cess', sa.SmallInteger(), nullable=True),
        sa.Column('invoice_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_id', 'seq')
    )
    op.create_index(op.f('ix_invoice_line_item_invoice_id'), 'invoice_line_item', ['invoice_id'], unique=False)
    op.add_column(u'item', sa.Column('cgst_tax_rate', sa.SmallInteger(), nullable=True))
    op.add_column(u'item', sa.Column('gst_compensation_cess', sa.SmallInteger(), nullable=True))
    op.add_column(u'item', sa.Column('gst_type', sa.SmallInteger(), nullable=True))
    op.add_column(u'item', sa.Column('hsn', sa.Unicode(length=255), nullable=True))
    op.add_column(u'item', sa.Column('igst_tax_rate', sa.SmallInteger(), nullable=True))
    op.add_column(u'item', sa.Column('sac', sa.Unicode(length=255), nullable=True))
    op.add_column(u'item', sa.Column('sgst_tax_rate', sa.SmallInteger(), nullable=True))
    op.add_column(u'item_collection', sa.Column('tax_type', sa.Unicode(length=80), nullable=True))


def downgrade():
    op.drop_column(u'item_collection', 'tax_type')
    op.drop_column(u'item', 'sgst_tax_rate')
    op.drop_column(u'item', 'sac')
    op.drop_column(u'item', 'igst_tax_rate')
    op.drop_column(u'item', 'hsn')
    op.drop_column(u'item', 'gst_type')
    op.drop_column(u'item', 'gst_compensation_cess')
    op.drop_column(u'item', 'cgst_tax_rate')
    op.drop_index(op.f('ix_invoice_line_item_invoice_id'), table_name='invoice_line_item')
    op.drop_table('invoice_line_item')
    op.drop_index(op.f('ix_invoice_customer_order_id'), table_name='invoice')
    op.drop_table('invoice')
