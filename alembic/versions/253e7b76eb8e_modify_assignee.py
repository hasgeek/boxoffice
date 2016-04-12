"""modify assignee

Revision ID: 253e7b76eb8e
Revises: 1ea1e8070ac8
Create Date: 2016-04-11 20:15:52.864916

"""

# revision identifiers, used by Alembic.
revision = '253e7b76eb8e'
down_revision = '1ea1e8070ac8'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.add_column('assignee', sa.Column('current', sa.Boolean(), nullable=True))
    op.create_check_constraint('assignee_current_check', 'assignee', u"current != '0'")
    op.add_column('assignee', sa.Column('line_item_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False))
    op.drop_index('assignee_email_key', table_name='assignee')
    op.create_unique_constraint('assignee_line_item_current_key', 'assignee', ['line_item_id', 'current'])
    op.drop_constraint(u'assignee_previous_id_fkey', 'assignee', type_='foreignkey')
    op.create_foreign_key('assignee_line_item_id', 'assignee', 'line_item', ['line_item_id'], ['id'])
    op.drop_column('assignee', 'previous_id')
    op.drop_constraint(u'line_item_assignee_id_fkey', 'line_item', type_='foreignkey')
    op.drop_column('line_item', 'assignee_id')


def downgrade():
    op.add_column('line_item', sa.Column('assignee_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'line_item_assignee_id_fkey', 'line_item', 'assignee', ['assignee_id'], ['id'])
    op.add_column('assignee', sa.Column('previous_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint('assignee_line_item_id', 'assignee', type_='foreignkey')
    op.create_foreign_key(u'assignee_previous_id_fkey', 'assignee', 'assignee', ['previous_id'], ['id'])
    op.drop_constraint('assignee_line_item_current_key', 'assignee', type_='unique')
    op.create_index('assignee_email_key', 'assignee', ['email'], unique=False)
    op.drop_column('assignee', 'line_item_id')
    op.drop_constraint('assignee_current_check', 'assignee')
    op.drop_column('assignee', 'current')
