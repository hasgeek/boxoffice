"""add discount_policy_id_to_line_item

Revision ID: c6619862211
Revises: 3e2221939085
Create Date: 2016-03-03 15:00:45.563998

"""

revision = 'c6619862211'
down_revision = '3e2221939085'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import coaster


def upgrade():
    op.add_column('line_item', sa.Column('discount_policy_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True))
    op.create_foreign_key('line_item_discount_policy_id_fk', 'line_item', 'discount_policy', ['discount_policy_id'], ['id'])


def downgrade():
    op.drop_constraint('line_item_discount_policy_id_fk', 'line_item', type_='foreignkey')
    op.drop_column('line_item', 'discount_policy_id')
