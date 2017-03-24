"""add_notes_to_payment_transaction

Revision ID: 1ea9ccd4bcc9
Revises: 4246213b032b
Create Date: 2017-03-24 12:30:44.365921

"""

# revision identifiers, used by Alembic.
revision = '1ea9ccd4bcc9'
down_revision = '4246213b032b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('payment_transaction', sa.Column('internal_note', sa.Text(), nullable=True))
    op.add_column('payment_transaction', sa.Column('note_to_user', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('payment_transaction', 'note_to_user')
    op.drop_column('payment_transaction', 'internal_note')
