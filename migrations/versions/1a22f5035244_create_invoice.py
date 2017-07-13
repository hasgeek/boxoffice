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
    op.add_column(u'item_collection', sa.Column('tax_type', sa.Unicode(length=80), nullable=True))


def downgrade():
    op.drop_column(u'item_collection', 'tax_type')
    op.drop_index(op.f('ix_invoice_customer_order_id'), table_name='invoice')
    op.drop_table('invoice')
