"""add_order_session

Revision ID: 45c2eb2f58ce
Revises: 510d2db2b008
Create Date: 2016-09-07 14:00:00.022841

"""

# revision identifiers, used by Alembic.
revision = '45c2eb2f58ce'
down_revision = '510d2db2b008'

import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('order_session',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('referrer', sa.Unicode(length=2083), nullable=True),
        sa.Column('utm_source', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_medium', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_term', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_content', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_id', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_campaign', sa.Unicode(length=250), nullable=False),
        sa.Column('gclid', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_session_customer_order_id'), 'order_session', ['customer_order_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_order_session_customer_order_id'), table_name='order_session')
    op.drop_table('order_session')
