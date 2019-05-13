"""add_order_session

Revision ID: 48e571c759cb
Revises: 510d2db2b008
Create Date: 2016-09-09 20:43:26.331871

"""

# revision identifiers, used by Alembic.
revision = '48e571c759cb'
down_revision = '510d2db2b008'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


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
    op.create_index(op.f('ix_order_session_gclid'), 'order_session', ['gclid'], unique=False)
    op.create_index(op.f('ix_order_session_utm_campaign'), 'order_session', ['utm_campaign'], unique=False)
    op.create_index(op.f('ix_order_session_utm_id'), 'order_session', ['utm_id'], unique=False)
    op.create_index(op.f('ix_order_session_utm_medium'), 'order_session', ['utm_medium'], unique=False)
    op.create_index(op.f('ix_order_session_utm_source'), 'order_session', ['utm_source'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_order_session_utm_source'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_utm_medium'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_utm_id'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_utm_campaign'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_gclid'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_customer_order_id'), table_name='order_session')
    op.drop_table('order_session')
