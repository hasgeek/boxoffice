"""add_trigram_index_for_discount_policy_title

Revision ID: 3a585b8d5f8d
Revises: 4246213b032b
Create Date: 2017-03-16 15:52:14.889764

"""

# revision identifiers, used by Alembic.
revision = '3a585b8d5f8d'
down_revision = '18576fdffd86'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.execute(sa.DDL(
        '''
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        CREATE INDEX idx_discount_policy_title_trgm on discount_policy USING gin (title gin_trgm_ops);
        '''))


def downgrade():
    op.drop_index('idx_discount_policy_title_trgm', 'discount_policy')
