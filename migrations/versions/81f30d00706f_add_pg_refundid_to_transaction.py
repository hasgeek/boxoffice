"""add_pg_refundid_to_transaction

Revision ID: 81f30d00706f
Revises: 1a22f5035244
Create Date: 2017-10-19 03:39:48.608087

"""

# revision identifiers, used by Alembic.
revision = '81f30d00706f'
down_revision = '1a22f5035244'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('payment_transaction', sa.Column('pg_refundid', sa.Unicode(length=80), nullable=True))
    op.create_index(op.f('ix_online_payment_pg_paymentid'), 'online_payment', ['pg_paymentid'], unique=True)
    op.create_index(op.f('ix_payment_transaction_pg_refundid'), 'payment_transaction', ['pg_refundid'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_payment_transaction_pg_refundid'), table_name='payment_transaction')
    op.drop_index(op.f('ix_online_payment_pg_paymentid'), table_name='online_payment')
    op.drop_column('payment_transaction', 'pg_refundid')
