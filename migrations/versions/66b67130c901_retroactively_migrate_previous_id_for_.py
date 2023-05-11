"""retroactively_migrate_previous_id_for_line_item.

Revision ID: 66b67130c901
Revises: 171fcb171759
Create Date: 2017-10-26 14:50:18.859247

"""

from collections import OrderedDict

from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '66b67130c901'
down_revision = '171fcb171759'


class LINE_ITEM_STATUS:  # noqa: N801
    CONFIRMED = 0
    CANCELLED = 1
    PURCHASE_ORDER = 2
    VOID = 3


class ORDER_STATUS:  # noqa: N801
    PURCHASE_ORDER = 0
    SALES_ORDER = 1
    INVOICE = 2
    CANCELLED = 3

    TRANSACTION = {SALES_ORDER, INVOICE, CANCELLED}


def find_nearest_timestamp(lst, timestamp):
    if not lst:
        return None
    nearest_ts = min(lst, key=lambda ts: abs(ts - timestamp).total_seconds())
    if abs(nearest_ts - timestamp).total_seconds() < 1:
        return nearest_ts


def set_previous_keys_for_line_items(line_items):
    timestamped_line_items = OrderedDict()

    # Assemble the `timestamped_line_items` dictionary with the timestamp at which the line items were created
    # as the key, and the line items that were created at that time as the value (as a list)
    # Some line items may have been created a few milliseconds later, so the nearest timestamp
    # with a tolerance level of one second is searched for
    for line_item in line_items:
        ts_key = (
            find_nearest_timestamp(
                list(timestamped_line_items.keys()), line_item.created_at
            )
            or line_item.created_at
        )
        if not timestamped_line_items.get(ts_key):
            timestamped_line_items[ts_key] = []
        timestamped_line_items[ts_key].append(
            {
                'id': line_item.id,
                'status': line_item.status,
                'item_id': line_item.item_id,
                'previous_id': None,
            }
        )

    # The previous line item for a line item, is a line item that has an earlier timestamp with a void status
    # with the same item_id. Find it and set it
    used_line_item_ids = set()
    for idx, (timestamp, _line_item_dicts) in enumerate(
        timestamped_line_items.items()[1:]
    ):
        # 0th timestamps are root line items, so they're skipped since
        # they don't need their `previous_id` to be updated
        for li_dict in timestamped_line_items[timestamp]:
            # timestamped_line_items.keys()[idx] and not timestamped_line_items.keys()[idx-1]
            # because the timestamped_line_items.items() list is enumerated from index 1
            previous_li_dict = [
                previous_li_dict
                for previous_li_dict in timestamped_line_items[
                    list(timestamped_line_items.keys())[idx]
                ]
                if previous_li_dict['item_id'] == li_dict['item_id']
                and previous_li_dict['id'] not in used_line_item_ids
                and previous_li_dict['status'] == LINE_ITEM_STATUS.VOID
            ][0]
            li_dict['previous_id'] = previous_li_dict['id']
            used_line_item_ids.add(previous_li_dict['id'])

    return [
        li_dict for li_dicts in timestamped_line_items.values() for li_dict in li_dicts
    ]


order_table = table(
    'customer_order',
    column('id', postgresql.UUID()),
    column('status', sa.Integer()),
)

line_item_table = table(
    'line_item',
    column('id', postgresql.UUID()),
    column('customer_order_id', postgresql.UUID()),
    column('item_id', postgresql.UUID()),
    column('previous_id', postgresql.UUID()),
    column('status', sa.Integer()),
    column('created_at', sa.Boolean()),
)


def upgrade():
    conn = op.get_bind()
    orders = conn.execute(
        sa.select(order_table.c.id)
        .where(order_table.c.status.in_(ORDER_STATUS.TRANSACTION))
        .select_from(order_table)
    )
    for order_id in [order.id for order in orders]:
        line_items = conn.execute(
            sa.select(
                [
                    line_item_table.c.id,
                    line_item_table.c.item_id,
                    line_item_table.c.status,
                    line_item_table.c.created_at,
                ]
            )
            .where(line_item_table.c.customer_order_id == order_id)
            .order_by(sa.text('created_at'))
            .select_from(line_item_table)
        )
        updated_line_item_dicts = set_previous_keys_for_line_items(line_items)
        for updated_line_item_dict in updated_line_item_dicts:
            if updated_line_item_dict['previous_id']:
                conn.execute(
                    sa.update(line_item_table)
                    .where(line_item_table.c.id == updated_line_item_dict['id'])
                    .values(previous_id=updated_line_item_dict['previous_id'])
                )


def downgrade():
    conn = op.get_bind()
    orders = conn.execute(
        sa.select(order_table.c.id)
        .where(order_table.c.status.in_(ORDER_STATUS.TRANSACTION))
        .select_from(order_table)
    )
    for order_id in [order.id for order in orders]:
        line_items = conn.execute(
            sa.select(line_item_table.c.id)
            .where(line_item_table.c.customer_order_id == order_id)
            .order_by(sa.text('created_at'))
            .select_from(line_item_table)
        )
        for line_item in line_items:
            conn.execute(
                sa.update(line_item_table)
                .where(line_item_table.c.id == line_item.id)
                .values(previous_id=None)
            )
