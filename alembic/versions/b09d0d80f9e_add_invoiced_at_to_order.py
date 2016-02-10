"""add invoiced_at to order

Revision ID: b09d0d80f9e
Revises: 4a7b87015bcb
Create Date: 2016-02-10 20:23:22.447874

"""

revision = 'b09d0d80f9e'
down_revision = '4a7b87015bcb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('order', sa.Column('invoiced_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('order', 'invoiced_at')
