"""add_fy_to_invoice.

Revision ID: 829f42c03de3
Revises: 23fc9e293ac3
Create Date: 2018-04-01 15:44:20.230030

"""

# revision identifiers, used by Alembic.
revision = '829f42c03de3'
down_revision = '23fc9e293ac3'

from alembic import op
from sqlalchemy.sql import column, table
import sqlalchemy as sa
import sqlalchemy_utils

from boxoffice.models.user import get_fiscal_year

invoice_table = table(
    'invoice',
    column('id', sqlalchemy_utils.types.uuid.UUIDType()),
    column('invoice_no', sa.Integer()),
    column('invoiced_at', sa.DateTime()),
    column('fy_start_at', sa.DateTime()),
    column('fy_end_at', sa.DateTime()),
)


def upgrade():
    conn = op.get_bind()
    op.add_column('invoice', sa.Column('fy_end_at', sa.DateTime(), nullable=True))
    op.add_column('invoice', sa.Column('fy_start_at', sa.DateTime(), nullable=True))
    op.drop_constraint(
        'invoice_organization_id_invoice_no_key', 'invoice', type_='unique'
    )
    op.create_unique_constraint(
        'invoice_organization_id_fy_start_at_fy_end_at_invoice_no_key',
        'invoice',
        ['organization_id', 'fy_start_at', 'fy_end_at', 'invoice_no'],
    )
    invoices = conn.execute(
        sa.select(invoice_table.c.id, invoice_table.c.invoiced_at).select_from(
            invoice_table
        )
    )
    for invoice in invoices:
        fy_start_at, fy_end_at = get_fiscal_year('in', invoice.invoiced_at)
        conn.execute(
            sa.update(invoice_table)
            .where(invoice_table.c.id == invoice.id)
            .values(fy_start_at=fy_start_at, fy_end_at=fy_end_at)
        )
    op.alter_column(
        'invoice', 'fy_start_at', existing_type=sa.DateTime(), nullable=False
    )
    op.alter_column('invoice', 'fy_end_at', existing_type=sa.DateTime(), nullable=False)


def downgrade():
    conn = op.get_bind()
    op.alter_column('invoice', 'fy_end_at', existing_type=sa.DateTime(), nullable=True)
    op.alter_column(
        'invoice', 'fy_start_at', existing_type=sa.DateTime(), nullable=True
    )
    invoices = conn.execute(sa.select(invoice_table.c.id).select_from(invoice_table))
    for invoice in invoices:
        conn.execute(
            sa.update(invoice_table)
            .where(invoice_table.c.id == invoice.id)
            .values(fy_start_at=None, fy_end_at=None)
        )
    op.drop_constraint(
        'invoice_organization_id_fy_start_at_fy_end_at_invoice_no_key',
        'invoice',
        type_='unique',
    )
    op.create_unique_constraint(
        'invoice_organization_id_invoice_no_key',
        'invoice',
        ['organization_id', 'invoice_no'],
    )
    op.drop_column('invoice', 'fy_start_at')
    op.drop_column('invoice', 'fy_end_at')
