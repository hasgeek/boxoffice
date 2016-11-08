"""add_transferrable_until

Revision ID: 8d205370475
Revises: 4246213b032b
Create Date: 2016-11-08 14:12:26.061615

"""

# revision identifiers, used by Alembic.
revision = '8d205370475'
down_revision = '4246213b032b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('item', sa.Column('transferrable_until', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('item', 'transferrable_until')
