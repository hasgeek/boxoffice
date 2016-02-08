"""add order to payment

Revision ID: 153722fa3bb2
Revises: 43f77492d922
Create Date: 2016-02-08 15:58:34.827249

"""

revision = '153722fa3bb2'
down_revision = '43f77492d922'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

def upgrade():
    op.add_column('payment', sa.Column('order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True))
    op.create_foreign_key(None, 'payment', 'order', ['order_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_column('payment', 'order_id')
