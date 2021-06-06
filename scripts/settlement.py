# settlements = {id: [{line_item_id, line_item_title, base_amount, final_amount}]}

from decimal import Decimal
import csv

from pytz import timezone, utc

from boxoffice.extapi.razorpay_status import RAZORPAY_PAYMENT_STATUS
from boxoffice.models import LINE_ITEM_STATUS, OnlinePayment, PaymentTransaction
from boxoffice.models.payment import TRANSACTION_TYPE


def csv_to_rows(csv_file, skip_header=True, delimiter=','):
    with open(csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        if skip_header:
            next(reader)
        return list(reader)


def rows_to_csv(rows, filename):
    with open(filename, 'wb') as csvfile:
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
            if not settlements.get('unsettled'):
                settlements['unsettled'] = []
            if trans[1] == 'payment':
                payment = OnlinePayment.query.filter_by(
                    pg_paymentid=trans[0],
                    pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED,
                ).first()
                if payment:
                    pt = PaymentTransaction.query.filter_by(
                        online_payment=payment,
                        transaction_type=TRANSACTION_TYPE.PAYMENT,
                    ).one_or_none()
                    # Get settlement
                    # settlement_amount = [tr for tr in transactions if tr[0] == trans[11]][0][4]
                    settlement = [tr for tr in transactions if tr[0] == trans[11]]
                    if settlement:
                        settlements[trans[11]].append(
                            {
                                'settlement_amount': settlement[0][4],
                                'settlement_date': trans[10],
                                'payment_id': payment.id,
                                'order_id': payment.customer_order_id,
                                'razorpay_fee': trans[6],
                                'razorpay_service_tax': trans[7],
                                'order_amount': trans[4],
                                'buyer_name': payment.order.buyer_fullname,
                                'transaction_date': localize(pt.created_at),
                                'receivable_amount': Decimal(pt.amount)
                                - Decimal(trans[6]),
                                'type': 'payment',
                            }
                        )
                    else:
                        settlements['unsettled'].append(
                            {
                                'settlement_amount': None,
                                'settlement_date': trans[10],
                                'payment_id': payment.id,
                                'order_id': payment.customer_order_id,
                                'razorpay_fee': trans[6],
                                'razorpay_service_tax': trans[7],
                                'order_amount': trans[4],
                                'buyer_name': payment.order.buyer_fullname,
                                'transaction_date': localize(pt.created_at),
                                'receivable_amount': Decimal(pt.amount)
                                - Decimal(trans[6]),
                                'type': 'payment',
                            }
                        )
                        print(  # NOQA: T001
                            "settlement not settled yet {settlement}".format(
                                settlement=trans[11]
                            )
                        )
                else:
                    print(  # NOQA: T001
                        "payment not found {payment}".format(payment=trans[0])
                    )
            elif trans[1] == 'refund':
                payment = OnlinePayment.query.filter_by(
                    pg_paymentid=trans[14],
                    pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED,
                ).first()
                if payment:
                    refund_transactions = PaymentTransaction.query.filter_by(
                        online_payment=payment, transaction_type=TRANSACTION_TYPE.REFUND
                    ).all()
                    # settlement_amount = [tr for tr in transactions if tr[0] == trans[11]][0][4]
                    settlement = [tr for tr in transactions if tr[0] == trans[11]]
                    if settlement:
                        for rt in refund_transactions:
                            settlements[trans[11]].append(
                                {
                                    'settlement_amount': settlement[0][4],
                                    'settlement_date': trans[10],
                                    'order_id': payment.customer_order_id,
                                    'razorpay_fee': trans[6],
                                    'razorpay_service_tax': trans[7],
                                    'order_amount': trans[4],
                                    'buyer_name': payment.order.buyer_fullname,
                                    'transaction_date': localize(rt.created_at),
                                    'receivable_amount': Decimal(0)
                                    - Decimal(rt.amount),
                                    'type': 'refund',
                                }
                            )
                    else:
                        for rt in refund_transactions:
                            settlements['unsettled'].append(
                                {
                                    'settlement_amount': None,
                                    'settlement_date': trans[10],
                                    'order_id': payment.customer_order_id,
                                    'razorpay_fee': trans[6],
                                    'razorpay_service_tax': trans[7],
                                    'order_amount': trans[4],
                                    'buyer_name': payment.order.buyer_fullname,
                                    'transaction_date': localize(rt.created_at),
                                    'receivable_amount': Decimal(0)
                                    - Decimal(rt.amount),
                                    'type': 'refund',
                                }
                            )
                        print(  # NOQA: T001
                            "settlement not settled yet {settlement}".format(
                                settlement=trans[11]
                            )
                        )
                else:
                    print(  # NOQA: T001
                        "payment not found {payment}".format(payment=trans[0])
                    )
            elif trans[1] == 'adjustment':
                settlement = [tr for tr in transactions if tr[0] == trans[11]]
                if settlement:
                    settlements[trans[11]].append(
                        {
                            'settlement_amount': settlement[0][4],
                            'settlement_date': trans[10],
                            'order_id': None,
                            'razorpay_fee': trans[6],
                            'razorpay_service_tax': trans[7],
                            'order_amount': None,
                            'buyer_name': "",
                            'transaction_date': None,
                            'receivable_amount': trans[3],
                            'type': 'adjustment',
                        }
                    )
                else:
                    print(  # NOQA: T001
                        "settlement not settled yet {settlement}".format(
                            settlement=trans[11]
                        )
                    )

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


def get_line_items(filename):
    # line_item_id, order_id, settlement_id, item_title
    transactions = csv_to_rows(filename)
    line_items = []
    header = [
        'line_item_id',
        'order_id',
        'settlement_id',
        'line_item_title',
        'cancelled',
    ]
    for trans in transactions:
        if trans[1] == 'payment':
            payment = OnlinePayment.query.filter_by(pg_paymentid=trans[0]).first()
            for line_item in payment.order.line_items:
                line_items.append(
                    [
                        line_item.id,
                        line_item.order.id,
                        trans[11],
                        line_item.item.title,
                        line_item.status == LINE_ITEM_STATUS.CANCELLED,
                    ]
                )

    line_items.insert(0, header)
    return line_items


def get_orders(settlement_filename):
    settlement_dicts = []
    # Load input data
    with open(settlement_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            settlement_dicts.append(row)

    # parse through input data
    payment_orders = []
    for settlement_dict in settlement_dicts:
        if settlement_dict['type'] == 'payment' and settlement_dict[
            'entity_id'
        ] not in [pord['entity_id'] for pord in payment_orders]:
            payment = OnlinePayment.query.filter_by(
                pg_paymentid=settlement_dict['entity_id'],
                pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED,
            ).one()
            payment_transaction = PaymentTransaction.query.filter_by(
                online_payment=payment, transaction_type=TRANSACTION_TYPE.PAYMENT
            ).one()
            payment_orders.append(
                {
                    'entity_id': settlement_dict['entity_id'],
                    'settlement_id': settlement_dict['settlement_id'],
                    'order_id': payment.order.id,
                    'buyer_fullname': payment.order.buyer_fullname,
                    'credit': settlement_dict['credit'],
                    'debit': '',
                    'fee': settlement_dict['fee'],
                    'receivable_amount': payment_transaction.amount
                    - Decimal(settlement_dict['fee']),
                    'settlement_date': settlement_dict['settled_at'],
                    'transaction_amount': payment_transaction.amount,
                    'transaction_date': localize(payment_transaction.created_at),
                }
            )
            if Decimal(
                settlement_dict['credit']
            ) != payment_transaction.amount - Decimal(settlement_dict['fee']):
                print("Tally failed for " + settlement_dict['entity_id'])  # NOQA: T001
        elif settlement_dict['type'] == 'refund' and settlement_dict[
            'entity_id'
        ] not in [pord['entity_id'] for pord in payment_orders]:
            try:
                payment = OnlinePayment.query.filter_by(
                    pg_paymentid=settlement_dict['payment_id'],
                    pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED,
                ).one()
                payment_transaction = PaymentTransaction.query.filter_by(
                    amount=Decimal(settlement_dict['debit']),
                    online_payment=payment,
                    transaction_type=TRANSACTION_TYPE.REFUND,
                ).first()
                if payment_transaction:
                    payment_orders.append(
                        {
                            'entity_id': settlement_dict['entity_id'],
                            'settlement_id': settlement_dict['settlement_id'],
                            'order_id': payment.order.id,
                            'buyer_fullname': payment.order.buyer_fullname,
                            'credit': '',
                            'debit': settlement_dict['debit'],
                            'fee': settlement_dict['fee'],
                            'receivable_amount': Decimal(0)
                            - Decimal(settlement_dict['debit']),
                            'settlement_date': settlement_dict['settled_at'],
                            'transaction_amount': Decimal(settlement_dict['debit']),
                            'transaction_date': localize(
                                payment_transaction.created_at
                            ),
                        }
                    )
                else:
                    print(  # NOQA: T001
                        "no transaction for " + settlement_dict['entity_id']
                    )
            except:  # NOQA: E722
                # FIXME: Trap the correct exception
                print(  # NOQA: T001
                    "no payment found for "
                    + settlement_dict['payment_id']
                    + "for entity "
                    + settlement_dict['entity_id']
                )

    # check if settlements tally
    for settlement_dict in [
        settlement_dict
        for settlement_dict in settlement_dicts
        if settlement_dict['type'] == 'settlement'
    ]:
        if Decimal(settlement_dict['amount']) != sum(
            [
                payment_order['receivable_amount']
                for payment_order in payment_orders
                if payment_order['settlement_id'] == settlement_dict['entity_id']
            ]
        ):
            print(  # NOQA: T001
                "Settlement not tallying for " + settlement_dict['entity_id']
            )

    # write result to csv
    with open('settlement_orders.csv', 'w') as outputcsv:
        fieldnames = [
            'entity_id',
            'settlement_id',
            'order_id',
            'buyer_fullname',
            'credit',
            'debit',
            'fee',
            'receivable_amount',
            'transaction_amount',
            'settlement_date',
            'transaction_date',
        ]
        writer = csv.DictWriter(outputcsv, fieldnames=fieldnames)
        writer.writeheader()
        for payment_order in payment_orders:
            writer.writerow(payment_order)
