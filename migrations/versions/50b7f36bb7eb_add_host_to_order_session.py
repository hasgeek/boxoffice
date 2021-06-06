"""add_host_to_order_session.

Revision ID: 50b7f36bb7eb
Revises: ca40e4eda72c
Create Date: 2019-12-06 10:38:43.256529

"""

# revision identifiers, used by Alembic.
revision = '50b7f36bb7eb'
down_revision = 'ca40e4eda72c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('order_session', sa.Column('host', sa.UnicodeText(), nullable=True))


def downgrade():
    op.drop_column('order_session', 'host')
