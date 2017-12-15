"""add_parent_organization

Revision ID: b3a8472f4668
Revises: 66b67130c901
Create Date: 2017-12-15 16:04:27.032259

"""

# revision identifiers, used by Alembic.
revision = 'b3a8472f4668'
down_revision = '66b67130c901'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('organization', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key('organization_parent_id_fkey', 'organization', 'organization', ['parent_id'], ['id'])


def downgrade():
    op.drop_constraint('organization_parent_id_fkey', 'organization', type_='foreignkey')
    op.drop_column('organization', 'parent_id')
