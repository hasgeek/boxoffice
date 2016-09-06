"""add_utm_campaign_to_order

Revision ID: 3ee98bac04f2
Revises: 510d2db2b008
Create Date: 2016-09-06 18:45:20.058362

"""

# revision identifiers, used by Alembic.
revision = '3ee98bac04f2'
down_revision = '510d2db2b008'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('customer_order', sa.Column('utm_campaign', sa.Unicode(length=80), nullable=True))


def downgrade():
    op.drop_column('customer_order', 'utm_campaign')
