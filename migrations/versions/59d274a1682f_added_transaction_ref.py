"""added_transaction_ref.

Revision ID: 59d274a1682f
Revises: 11bc47d6d60b
Create Date: 2016-06-28 21:34:21.889537

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '59d274a1682f'
down_revision = '11bc47d6d60b'


def upgrade():
    op.add_column(
        'payment_transaction',
        sa.Column('transaction_ref', sa.Unicode(length=80), nullable=True),
    )


def downgrade():
    op.drop_column('payment_transaction', 'transaction_ref')
