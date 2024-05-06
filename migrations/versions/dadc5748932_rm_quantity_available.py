"""
rm quantity_available.

Revision ID: dadc5748932
Revises: 253e7b76eb8e
Create Date: 2016-06-10 17:53:52.113035

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = 'dadc5748932'
down_revision = '253e7b76eb8e'


item = table(
    'item',
    column('id', postgresql.UUID()),
    column('quantity_total', sa.Integer()),
    column('quantity_available', sa.Integer()),
)

line_item = table(
    'line_item',
    column('item_id', postgresql.UUID()),
    column('status', sa.Integer()),
)


def upgrade() -> None:
    op.drop_constraint('item_quantity_available_lte_quantity_total_check', 'item')
    op.drop_column('item', 'quantity_available')


def downgrade() -> None:
    op.add_column(
        'item',
        sa.Column(
            'quantity_available', sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.execute(
        item.update().values(
            {
                'quantity_available': item.c.quantity_total
                - sa.select(sa.func.count())
                .select_from(line_item)
                .where(line_item.c.item_id == item.c.id)
                .where(line_item.c.status == 0)
                .scalar_subquery()
            }
        )
    )
    op.alter_column('item', 'quantity_available', nullable=False)
    op.create_check_constraint(
        'item_quantity_available_lte_quantity_total_check',
        'item',
        "quantity_available <= quantity_total",
    )
