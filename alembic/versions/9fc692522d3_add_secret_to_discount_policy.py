"""add_secret_to_discount_policy

Revision ID: 9fc692522d3
Revises: 510d2db2b008
Create Date: 2016-07-22 16:13:25.828665

"""

# revision identifiers, used by Alembic.
revision = '9fc692522d3'
down_revision = '510d2db2b008'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('discount_policy', sa.Column('secret', sa.Unicode(length=50), nullable=True))


def downgrade():
    op.drop_column('discount_policy', 'secret')
