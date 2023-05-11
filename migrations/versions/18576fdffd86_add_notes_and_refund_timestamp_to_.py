"""add_notes_and_refund_timestamp_to_transaction.

Revision ID: 18576fdffd86
Revises: 4246213b032b
Create Date: 2017-03-25 12:16:09.459952

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '18576fdffd86'
down_revision = '4246213b032b'


def upgrade():
    op.add_column(
        'payment_transaction',
        sa.Column('internal_note', sa.Unicode(length=250), nullable=True),
    )
    op.add_column(
        'payment_transaction',
        sa.Column('refund_description', sa.Unicode(length=250), nullable=True),
    )
    op.add_column(
        'payment_transaction',
        sa.Column('note_to_user_html', sa.UnicodeText(), nullable=True),
    )
    op.add_column(
        'payment_transaction',
        sa.Column('note_to_user_text', sa.UnicodeText(), nullable=True),
    )
    op.add_column(
        'payment_transaction', sa.Column('refunded_at', sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column('payment_transaction', 'refunded_at')
    op.drop_column('payment_transaction', 'note_to_user_text')
    op.drop_column('payment_transaction', 'note_to_user_html')
    op.drop_column('payment_transaction', 'refund_description')
    op.drop_column('payment_transaction', 'internal_note')
