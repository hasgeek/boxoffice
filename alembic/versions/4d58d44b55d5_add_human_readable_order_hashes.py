"""Add human readable order hashes

Revision ID: 4d58d44b55d5
Revises: b09d0d80f9e
Create Date: 2016-02-10 21:14:54.757818

"""

# revision identifiers, used by Alembic.
revision = '4d58d44b55d5'
down_revision = 'b09d0d80f9e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('order', sa.Column('order_hash', sa.Unicode(length=120), nullable=True))


def downgrade():
    op.drop_column('order', 'order_hash')
