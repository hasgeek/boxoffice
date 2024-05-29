"""
add_invoice_organization.

Revision ID: 23fc9e293ac3
Revises: 66b67130c901
Create Date: 2017-12-19 14:25:56.581176

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '23fc9e293ac3'
down_revision = '66b67130c901'


def upgrade() -> None:
    op.add_column('organization', sa.Column('invoicer_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'organization_invoicer_id_id_fkey',
        'organization',
        'organization',
        ['invoicer_id'],
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'organization_invoicer_id_id_fkey', 'organization', type_='foreignkey'
    )
    op.drop_column('organization', 'invoicer_id')
