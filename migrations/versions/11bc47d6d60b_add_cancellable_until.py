"""add cancellable_until.

Revision ID: 11bc47d6d60b
Revises: dadc5748932
Create Date: 2016-06-23 16:26:53.590750

"""

# revision identifiers, used by Alembic.
revision = '11bc47d6d60b'
down_revision = 'dadc5748932'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('item', sa.Column('cancellable_until', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('item', 'cancellable_until')
