"""add_transferrable_until

Revision ID: 6a6c0be09f
Revises: 48e571c759cb
Create Date: 2016-09-13 18:12:25.445124

"""

# revision identifiers, used by Alembic.
revision = '6a6c0be09f'
down_revision = '48e571c759cb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('item', sa.Column('transferrable_until', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('item', 'transferrable_until')
