"""add organization id to item

Revision ID: 193d0f40c6
Revises: 1d7b9fea0406
Create Date: 2016-01-28 13:31:54.750325

"""

# revision identifiers, used by Alembic.
revision = '193d0f40c6'
down_revision = '1d7b9fea0406'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('item', sa.Column('organization_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'item', 'organization', ['organization_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_column('item', 'organization_id')
