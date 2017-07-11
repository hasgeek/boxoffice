"""invoice_fields_for_org

Revision ID: c6d307e5fd4c
Revises: 1a22f5035244
Create Date: 2017-07-11 12:56:04.709091

"""

# revision identifiers, used by Alembic.
revision = 'c6d307e5fd4c'
down_revision = '1a22f5035244'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('organization', sa.Column('fy_start_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('organization', 'fy_start_at')
