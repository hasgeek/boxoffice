"""Switch to timestamptz.

Revision ID: cdb214cf1e06
Revises: 7d180b95fcbe
Create Date: 2019-05-15 20:57:30.620521

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cdb214cf1e06'
down_revision = '7d180b95fcbe'


migrate_table_columns = [
    ('assignee', 'created_at'),
    ('assignee', 'updated_at'),
    ('category', 'created_at'),
    ('category', 'updated_at'),
    ('customer_order', 'cancelled_at'),
    ('customer_order', 'created_at'),
    ('customer_order', 'initiated_at'),
    ('customer_order', 'invoiced_at'),
    ('customer_order', 'paid_at'),
    ('customer_order', 'updated_at'),
    ('discount_policy', 'created_at'),
    ('discount_policy', 'updated_at'),
    ('invoice', 'created_at'),
    ('invoice', 'fy_end_at'),
    ('invoice', 'fy_start_at'),
    ('invoice', 'invoiced_at'),
    ('invoice', 'updated_at'),
    ('item', 'cancellable_until'),
    ('item', 'created_at'),
    ('item', 'updated_at'),
    ('item_collection', 'created_at'),
    ('item_collection', 'updated_at'),
    ('item_discount_policy', 'created_at'),
    ('line_item', 'cancelled_at'),
    ('line_item', 'created_at'),
    ('line_item', 'ordered_at'),
    ('line_item', 'updated_at'),
    ('online_payment', 'confirmed_at'),
    ('online_payment', 'created_at'),
    ('online_payment', 'failed_at'),
    ('online_payment', 'updated_at'),
    ('order_session', 'created_at'),
    ('order_session', 'updated_at'),
    ('organization', 'created_at'),
    ('organization', 'updated_at'),
    ('payment_transaction', 'created_at'),
    ('payment_transaction', 'refunded_at'),
    ('payment_transaction', 'updated_at'),
    ('price', 'created_at'),
    ('price', 'end_at'),
    ('price', 'start_at'),
    ('price', 'updated_at'),
    ('user', 'created_at'),
    ('user', 'updated_at'),
]


def upgrade():
    for table, column in migrate_table_columns:
        op.execute(
            sa.DDL(
                'ALTER TABLE "%(table)s" ALTER COLUMN "%(column)s"'
                'TYPE TIMESTAMP WITH TIME ZONE USING "%(column)s" AT TIME ZONE \'UTC\'',
                context={'table': table, 'column': column},
            )
        )


def downgrade():
    for table, column in reversed(migrate_table_columns):
        op.execute(
            sa.DDL(
                'ALTER TABLE "%(table)s" ALTER COLUMN "%(column)s"'
                ' TYPE TIMESTAMP WITHOUT TIME ZONE',
                context={'table': table, 'column': column},
            )
        )
