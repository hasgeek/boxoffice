import csv
from decimal import Decimal

from boxoffice.models import (
    LineItem,
    LineItemStatus,
    OnlinePayment,
    RazorpayPaymentStatus,
)


def line_item_is_cancelled(line_item):
    return line_item.status == LineItemStatus.CANCELLED


def order_net_amount(order):
    return order.get_amounts().final_amount - sum(
        line_item.final_amount
        for line_item in order.line_items
        if line_item_is_cancelled(line_item)
    )


def get_settled_orders(settlement_files):
    entity_dict = {}
    for settlement_filename in settlement_files:
        # Load input data
        with open(settlement_filename, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not entity_dict.get(row['entity_id']):
                    entity_dict[row['entity_id']] = row

    def format_row(row):
        fields = [
            'settlement_id',
            'order_id',
            'payment_id',
            'line_item_id',
            'ticket_title',
            'base_amount',
            'discounted_amount',
            'final_amount',
            'transaction_date',
            'payment_status',
            'settled_at',
            'razorpay_fees',
            'order_amount',
            'receivable_amount',
            'settlement_amount',
            'buyer_fullname',
        ]
        for field in fields:
            if not row.get(field):
                row[field] = '-'
        return row

    def format_line_item(settlement_id, payment_id, line_item, payment_status):
        transaction_date = (
            line_item.ordered_at if line_item.is_confirmed else line_item.cancelled_at
        )
        return {
            'settlement_id': settlement_id,
            'order_id': line_item.order.id,
            'payment_id': payment_id,
            'line_item_id': line_item.id,
            'ticket_title': line_item.ticket.title,
            'base_amount': line_item.base_amount,
            'discounted_amount': line_item.discounted_amount,
            'final_amount': line_item.final_amount,
            'payment_status': payment_status,
            'transaction_date': transaction_date,
        }

    settlement_ids = [
        entity['entity_id']
        for entity in entity_dict.values()
        if entity['type'] == 'settlement'
    ]
    settled_orders = []
    for settlement_id in settlement_ids:
        settled_orders.append(
            format_row(
                {
                    'settlement_id': settlement_id,
                    'settlement_amount': entity_dict[settlement_id]['amount'],
                    'settled_at': entity_dict[settlement_id]['settled_at'],
                }
            )
        )
        settlement_payment_ids = [
            entity['entity_id']
            for entity in entity_dict.values()
            if entity['type'] == 'payment' and entity['settlement_id'] == settlement_id
        ]
        for settlement_payment_id in settlement_payment_ids:
            payment = OnlinePayment.query.filter(
                OnlinePayment.pg_paymentid == settlement_payment_id,
                OnlinePayment.pg_payment_status == RazorpayPaymentStatus.CAPTURED,
            ).one()
            order = payment.order
            settled_orders.append(
                format_row(
                    {
                        'settlement_id': settlement_id,
                        'order_id': order.id,
                        'order_amount': order_net_amount(order),
                        'buyer_fullname': order.buyer_fullname,
                        'payment_id': payment.pg_paymentid,
                        'razorpay_fees': entity_dict[payment.pg_paymentid]['fee'],
                        'receivable_amount': order_net_amount(order)
                        - Decimal(entity_dict[payment.pg_paymentid]['fee']),
                    }
                )
            )

            for line_item in order.line_items:
                settled_orders.append(
                    format_row(
                        format_line_item(
                            settlement_id, settlement_payment_id, line_item, 'payment'
                        )
                    )
                )
                # if line_item_is_cancelled(line_item):
                #     settled_orders.append(
                #         format_row(
                #             format_line_item(
                #                 settlement_id,
                #                 settlement_payment_id,
                #                 line_item,
                #                 'refund',
                #             )
                #         )
                #     )

        settlement_refund_ids = [
            entity['entity_id']
            for entity in entity_dict.values()
            if entity['type'] == 'refund' and entity['settlement_id'] == settlement_id
        ]
        for settlement_refund_id in settlement_refund_ids:
            payment = OnlinePayment.query.filter(
                OnlinePayment.pg_paymentid
                == entity_dict[settlement_refund_id]['payment_id'],
                OnlinePayment.pg_payment_status == RazorpayPaymentStatus.CAPTURED,
            ).one()
            order = payment.order
            settled_orders.append(
                format_row(
                    {
                        'settlement_id': settlement_id,
                        'order_id': order.id,
                        'order_amount': order_net_amount(order),
                        'buyer_fullname': order.buyer_fullname,
                        'payment_id': payment.pg_paymentid,
                        'razorpay_fees': Decimal('0'),
                        'receivable_amount': Decimal('0')
                        - Decimal(entity_dict[settlement_refund_id]['debit']),
                    }
                )
            )
            # HACK, fetching by amount in an order
            try:
                cancelled_line_item = LineItem.query.filter(
                    LineItem.order == order,
                    LineItem.final_amount
                    == Decimal(entity_dict[settlement_refund_id]['debit']),
                    LineItem.status == LineItemStatus.CANCELLED,
                ).one()
                settled_orders.append(
                    format_row(
                        format_line_item(
                            settlement_id,
                            settlement_refund_id,
                            cancelled_line_item,
                            'refund',
                        )
                    )
                )
            except:  # noqa: E722  # pylint: disable=bare-except
                # FIXME: Add correct exception
                print("Multiple line items found")  # noqa: T201
                print(payment.pg_paymentid)  # noqa: T201
                cancelled_line_item = LineItem.query.filter(
                    LineItem.order == order,
                    LineItem.final_amount
                    == Decimal(entity_dict[settlement_refund_id]['debit']),
                    LineItem.status == LineItemStatus.CANCELLED,
                ).one_or_none()
                if cancelled_line_item is not None:
                    settled_orders.append(
                        format_row(
                            format_line_item(
                                settlement_id,
                                settlement_refund_id,
                                cancelled_line_item,
                                'refund',
                            )
                        )
                    )
                else:
                    print("no line item found")  # noqa: T201
                    print(payment.pg_paymentid)  # noqa: T201

    return settled_orders


def write_settled_orders(filename, rows) -> None:
    with open(filename, 'w', encoding='utf-8') as csvfile:
        fieldnames = [
            'settlement_id',
            'order_id',
            'payment_id',
            'line_item_id',
            'item_title',
            'base_amount',
            'discounted_amount',
            'final_amount',
            'transaction_date',
            'payment_status',
            'settled_at',
            'razorpay_fees',
            'order_amount',
            'receivable_amount',
            'settlement_amount',
            'buyer_fullname',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
