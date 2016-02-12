"""add cancelled_at to order

Revision ID: 2b514fd5685f
Revises: 4b7c29e3fca2
Create Date: 2016-02-12 16:19:27.955645

"""

# revision identifiers, used by Alembic.
revision = '2b514fd5685f'
down_revision = '4b7c29e3fca2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('customer_order', sa.Column('cancelled_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('customer_order', 'cancelled_at')
