# settlements = {id: [{line_item_id, line_item_title, base_amount, final_amount}]}

from decimal import Decimal
import csv

from pytz import timezone, utc

from boxoffice.models import OnlinePayment, PaymentTransaction
from boxoffice.models.payment import TRANSACTION_TYPE

# init_for('dev')


def csv_to_rows(csv_file, skip_header=True, delimiter=','):
    with open(csv_file, 'rb', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        if skip_header:
            next(reader)
        return list(reader)


def rows_to_csv(rows, filename):
    with open(filename, 'wb', encoding='utf-8') as csvfile:
        writer = csv.writer(
            csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for row in rows:
            writer.writerow(row)
        return True


def localize(datetime):
    if datetime.tzinfo is None:
        datetime = utc.localize(datetime)
    return datetime.astimezone(timezone('Asia/Kolkata')).strftime('%d %b, %Y')


def get_settlements(filename):
    settlements = {}
    transactions = csv_to_rows(filename)

    for trans in transactions:
        if trans[11]:
            # if settlements has this settlement_id as a key
            if not settlements.get(trans[11]):
                settlements[trans[11]] = []
            if trans[1] == 'payment':
                payment = OnlinePayment.query.filter_by(pg_paymentid=trans[0]).first()
                if payment:
                    pt = PaymentTransaction.query.filter_by(
                        online_payment=payment,
                        transaction_type=TRANSACTION_TYPE.PAYMENT,
                    ).one_or_none()
                    # Get settlement
                    settlement_amount = [
                        tr for tr in transactions if tr[0] == trans[11]
                    ][0][4]
                    settlements[trans[11]].append(
                        {
                            'settlement_amount': settlement_amount,
                            'settlement_date': trans[10],
                            'payment_id': payment.id,
                            'order_id': payment.customer_order_id,
                            'razorpay_fee': trans[6],
                            'razorpay_service_tax': trans[7],
                            'order_amount': trans[4],
                            'buyer_name': payment.order.buyer_fullname,
                            'transaction_date': localize(pt.created_at),
                            'receivable_amount': Decimal(pt.amount) - Decimal(trans[6]),
                            'type': 'payment',
                        }
                    )
                else:
                    print(trans[0])  # noqa: T201
            elif trans[1] == 'refund':
                payment = OnlinePayment.query.filter_by(pg_paymentid=trans[14]).first()
                if payment:
                    refund_transactions = PaymentTransaction.query.filter_by(
                        online_payment=payment, transaction_type=TRANSACTION_TYPE.REFUND
                    ).all()
                    settlement_amount = [
                        tr for tr in transactions if tr[0] == trans[11]
                    ][0][4]
                    for rt in refund_transactions:
                        settlements[trans[11]].append(
                            {
                                'settlement_amount': settlement_amount,
                                'settlement_date': trans[10],
                                'order_id': payment.customer_order_id,
                                'razorpay_fee': trans[6],
                                'razorpay_service_tax': trans[7],
                                'order_amount': trans[4],
                                'buyer_name': payment.order.buyer_fullname,
                                'transaction_date': localize(rt.created_at),
                                'receivable_amount': Decimal(0) - Decimal(rt.amount),
                                'type': 'refund',
                            }
                        )
                else:
                    print(trans[0])  # noqa: T201

    rows = []
    header = [
        'settlement_id',
        'settlement_amount',
        'settlement_date',
        'order_id',
        'razorpay_fee',
        'razorpay_service_tax',
        'order_amount',
        'buyer_name',
        'transaction_date',
        'receivable_amount',
        'type',
    ]
    for stmt, stm_transactions in settlements.items():
        for details in stm_transactions:
            rows.append(
                [
                    stmt,
                    details['settlement_amount'],
                    details['settlement_date'],
                    details['order_id'],
                    details['razorpay_fee'],
                    details['razorpay_service_tax'],
                    details['order_amount'],
                    details['buyer_name'],
                    details['transaction_date'],
                    details['receivable_amount'],
                    details['type'],
                ]
            )
    rows.insert(0, header)
    return rows


# yoga_pay_orders = []
# for yt in yoga_trans:
#     pay = OnlinePayment.query.filter_by(pg_paymentid=yt[0]).first()
#     yoga_pay_orders.append(
#         [yt[0], pay.order.buyer_fullname, float(yt[4]), float(yt[6])]
#     )

# yoga_pay_orders = []
# for yt in yoga_trans:
#     pay = OnlinePayment.query.filter_by(pg_paymentid=yt[0]).first()
#     for li in pay.order.line_items:
#         yoga_pay_orders.append(
#             [
#                  yt[0],
#                  pay.order.buyer_fullname,
#                  float(yt[4]),
#                  float(yt[6]),
#                  li.item.title
#             ]
#         )

# yoga_pay_orders = []
# for yt in yoga_trans:
#     pay = OnlinePayment.query.filter_by(pg_paymentid=yt[0]).first()
#     for li in pay.order.line_items:
#         yoga_pay_orders.append(
#             [
#                 yt[0],
#                 pay.order.id,
#                 pay.order.buyer_fullname,
#                 yt[4],
#                 yt[6],
#                 yt[7],
#                 li.item.title,
#                 unicode(li.final_amount),
#                 localize(pay.created_at),
#             ]
#         )

# for oid in oids:
#     oids_dict[oid] = {
#         'amount': [yp[3] for yp in yoga_pay_orders if yp[1] == oid][0],
#         'fee': [yp[4] for yp in yoga_pay_orders if yp[1] == oid][0],
#     }

# yoga_pay_orders = []
# for yt in yoga_trans:
#     pay = OnlinePayment.query.filter_by(pg_paymentid=yt[0]).first()
#     order_id = json.loads(yoga_trans[0][-2])
#     order = Order.query.get(order_id['order_id'])
#     for li in order.line_items:
#         yoga_pay_orders.append(
#             [
#                 yt[0],
#                 order.id,
#                 order.buyer_fullname,
#                 yt[4],
#                 yt[6],
#                 yt[7],
#                 li.item.title,
#                 unicode(li.final_amount),
#                 localize(pay.created_at),
#             ]
#         )
