"""add_previous_to_line_item

Revision ID: 171fcb171759
Revises: 81f30d00706f
Create Date: 2017-10-24 18:40:39.183620

"""

# revision identifiers, used by Alembic.
revision = '171fcb171759'
down_revision = '81f30d00706f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils

def upgrade():
    op.add_column('line_item', sa.Column('previous_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=True))
    op.create_index(op.f('ix_line_item_previous_id'), 'line_item', ['previous_id'], unique=False)
    op.create_foreign_key('line_item_id_fkey', 'line_item', 'line_item', ['previous_id'], ['id'])
    op.create_unique_constraint('line_item_previous_id_key', 'line_item', ['previous_id'])


def downgrade():
    op.drop_constraint('line_item_previous_id_key', 'line_item', type_='unique')
    op.drop_constraint('line_item_id_fkey', 'line_item', type_='foreignkey')
    op.drop_index(op.f('ix_line_item_previous_id'), table_name='line_item')
    op.drop_column('line_item', 'previous_id')
