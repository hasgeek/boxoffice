"""create_invoice

Revision ID: e3358f4bfd74
Revises: 36f458047cfd
Create Date: 2017-07-03 18:39:08.883749

"""

# revision identifiers, used by Alembic.
revision = 'e3358f4bfd74'
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
        sa.Column('street_address', sa.Unicode(length=255), nullable=True),
        sa.Column('city', sa.Unicode(length=255), nullable=True),
        sa.Column('state', sa.Unicode(length=255), nullable=True),
        sa.Column('country', sa.Unicode(length=255), nullable=True),
        sa.Column('postcode', sa.Unicode(length=255), nullable=True),
        sa.Column('taxid', sa.Unicode(length=255), nullable=True),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_customer_order_id'), 'invoice', ['customer_order_id'], unique=False)
    op.add_column(u'item_collection', sa.Column('tax_type', sa.Unicode(length=80), nullable=True))


def downgrade():
    op.drop_column(u'item_collection', 'tax_type')
    op.drop_index(op.f('ix_invoice_customer_order_id'), table_name='invoice')
    op.drop_table('invoice')
