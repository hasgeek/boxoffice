"""add seq to item

Revision ID: 74770336785
Revises: 59d274a1682f
Create Date: 2016-07-06 10:09:49.553138

"""

# revision identifiers, used by Alembic.
revision = '74770336785'
down_revision = '59d274a1682f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('item', sa.Column('seq', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('item', 'seq')
