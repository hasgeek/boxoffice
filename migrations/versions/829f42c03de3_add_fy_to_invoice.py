"""
add_fy_to_invoice.

Revision ID: 829f42c03de3
Revises: 23fc9e293ac3
Create Date: 2018-04-01 15:44:20.230030

"""

from datetime import datetime

import pytz
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = '829f42c03de3'
down_revision = '23fc9e293ac3'


def naive_to_utc(
    dt: datetime, timezone: str | pytz.BaseTzInfo | None = None
) -> datetime:
    """
    Return a UTC datetime for a given naive datetime or date object.

    Localizes it to the given timezone and converts it into a UTC datetime
    """
    if timezone:
        tz = pytz.timezone(timezone) if isinstance(timezone, str) else timezone
    elif isinstance(dt, datetime) and dt.tzinfo:
        tz = dt.tzinfo  # type: ignore[assignment]
    else:
        tz = pytz.UTC

    return tz.localize(dt).astimezone(tz).astimezone(pytz.UTC)


def get_fiscal_year(jurisdiction: str, dt: datetime) -> tuple[datetime, datetime]:
    """
    Return the financial year for a given jurisdiction and timestamp.

    Returns start and end dates as tuple of timestamps. Recognizes April 1 as the start
    date for India (jurisfiction code: 'in'), January 1 everywhere else.

    Example::

        get_fiscal_year('IN', utcnow())
    """
    if jurisdiction.lower() == 'in':
        start_year = dt.year - 1 if dt.month < 4 else dt.year
        # starts on April 1 XXXX
        fy_start = datetime(start_year, 4, 1)
        # ends on April 1 XXXX + 1
        fy_end = datetime(start_year + 1, 4, 1)
        timezone = 'Asia/Kolkata'
        return (naive_to_utc(fy_start, timezone), naive_to_utc(fy_end, timezone))
    return (
        naive_to_utc(datetime(dt.year, 1, 1)),
        naive_to_utc(datetime(dt.year + 1, 1, 1)),
    )


invoice_table = table(
    'invoice',
    column('id', postgresql.UUID()),
    column('invoice_no', sa.Integer()),
    column('invoiced_at', sa.DateTime()),
    column('fy_start_at', sa.DateTime()),
    column('fy_end_at', sa.DateTime()),
)


def upgrade() -> None:
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


def downgrade() -> None:
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
