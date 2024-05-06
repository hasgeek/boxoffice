"""
make contact_email non nullable.

Revision ID: 4d7f840202d2
Revises: 27b5ed98d7d0
Create Date: 2016-03-25 16:44:42.974915

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4d7f840202d2'
down_revision = '27b5ed98d7d0'


def upgrade() -> None:
    op.alter_column(
        'organization',
        'contact_email',
        existing_type=sa.VARCHAR(length=254),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'organization',
        'contact_email',
        existing_type=sa.VARCHAR(length=254),
        nullable=True,
    )
