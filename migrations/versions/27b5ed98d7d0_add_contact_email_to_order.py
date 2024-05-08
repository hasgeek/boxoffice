"""
add contact_email to order.

Revision ID: 27b5ed98d7d0
Revises: 4ffee334e82e
Create Date: 2016-03-25 14:40:26.194351

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '27b5ed98d7d0'
down_revision = '4ffee334e82e'


def upgrade() -> None:
    op.add_column(
        'organization',
        sa.Column('contact_email', sa.Unicode(length=254), nullable=True),
    )
    op.create_unique_constraint(
        'organization_contact_email_key', 'organization', ['contact_email']
    )


def downgrade() -> None:
    op.drop_constraint('organization_contact_email_key', 'organization', type_='unique')
    op.drop_column('organization', 'contact_email')
