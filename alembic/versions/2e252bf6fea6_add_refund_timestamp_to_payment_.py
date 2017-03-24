"""add_refund_timestamp_to_payment_transaction

Revision ID: 2e252bf6fea6
Revises: 1ea9ccd4bcc9
Create Date: 2017-03-24 13:39:45.812428

"""

# revision identifiers, used by Alembic.
revision = '2e252bf6fea6'
down_revision = '1ea9ccd4bcc9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('payment_transaction', sa.Column('refunded_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('payment_transaction', 'refunded_at')
