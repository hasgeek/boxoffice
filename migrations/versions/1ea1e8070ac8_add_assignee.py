"""add assignee.

Revision ID: 1ea1e8070ac8
Revises: adb90a264e3
Create Date: 2016-04-09 11:53:52.668646

"""

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1ea1e8070ac8'
down_revision = 'adb90a264e3'


def upgrade():
    op.create_table(
        'assignee',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('fullname', sa.Unicode(length=80), nullable=False),
        sa.Column('email', sa.Unicode(length=254), nullable=False),
        sa.Column('phone', sa.Unicode(length=16), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=False),
        sa.Column('previous_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['previous_id'],
            ['assignee.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.add_column('line_item', sa.Column('assignee_id', sa.Integer(), nullable=True))
    op.add_column(
        'item',
        sa.Column(
            'assignee_details', postgresql.JSONB(), server_default='{}', nullable=True
        ),
    )
    op.alter_column('item', 'assignee_details', server_default=None)
    op.create_foreign_key(
        'line_item_assignee_id_fkey', 'line_item', 'assignee', ['assignee_id'], ['id']
    )
    op.create_index(op.f('assignee_email_key'), 'assignee', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('assignee_email_key'), table_name='assignee')
    op.drop_constraint('line_item_assignee_id_fkey', 'line_item', type_='foreignkey')
    op.drop_column('item', 'assignee_details')
    op.drop_column('line_item', 'assignee_id')
    op.drop_table('assignee')
