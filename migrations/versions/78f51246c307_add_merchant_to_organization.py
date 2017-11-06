"""add_merchant_to_organization

Revision ID: 78f51246c307
Revises: 66b67130c901
Create Date: 2017-10-31 17:07:38.948128

"""

# revision identifiers, used by Alembic.
revision = '78f51246c307'
down_revision = '66b67130c901'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column
import sqlalchemy_utils

organization_table = table('organization',
    column('id', sqlalchemy_utils.types.uuid.UUIDType()),
    column('merchant', sa.Boolean())
)


def upgrade():
    op.add_column('organization', sa.Column('merchant', sa.Boolean(), nullable=True))
    op.execute(organization_table.update().values({'merchant': False}))  # noqa
    op.alter_column('organization', 'merchant', nullable=False)

def downgrade():
    op.drop_column('organization', 'merchant')
