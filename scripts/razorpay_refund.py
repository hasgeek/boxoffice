import csv

import pytz
import requests

from boxoffice import app
from boxoffice.models import RAZORPAY_PAYMENT_STATUS, OnlinePayment


def get_refunds(date_ranges):
    """
    Return a list of rows containing refund details.

    Keys: refund_transaction_id, refund_description, amount, refunded_at, payment_id,
    settlement_id, order_id
    """
    entity_dict = {}
    entities = []
    settlements_url = 'https://api.razorpay.com/v1/settlements/report/combined'
    refunds = []

    for date_range in date_ranges:
        settlement_resp = requests.get(
            settlements_url,
            params={'year': date_range['year'], 'month': date_range['month']},
            auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']),
            timeout=30,
        )
        entities = settlement_resp.json()

    for entity in [entity for entity in entities if entity is not None]:
        if not entity_dict.get(entity['entity_id']):
            entity_dict[entity['entity_id']] = entity

    settlement_ids = [
        entity['entity_id']
        for entity in entity_dict.values()
        if entity['type'] == 'settlement'
    ]
    for settlement_id in settlement_ids:
        settlement_refund_ids = [
            entity['entity_id']
            for entity in entity_dict.values()
            if entity['type'] == 'refund' and entity['settlement_id'] == settlement_id
        ]
        for settlement_refund_id in settlement_refund_ids:
            payment = OnlinePayment.query.filter(
                OnlinePayment.pg_paymentid
                == entity_dict[settlement_refund_id]['payment_id'],
                OnlinePayment.pg_payment_status == RAZORPAY_PAYMENT_STATUS.CAPTURED,
            ).one()
            order = payment.order
            for refund_transaction in order.refund_transactions:
                refunds.append(
                    {
                        'transaction_id': refund_transaction.id,
                        'settlement_id': settlement_id,
                        'order_id': order.id,
                        'order_date': pytz.timezone('Asia/Kolkata')
                        .localize(order.paid_at)
                        .strftime('%d %b %Y'),
                        'amount': refund_transaction.amount,
                        'refunded_at': pytz.timezone('Asia/Kolkata')
                        .localize(refund_transaction.created_at)
                        .strftime('%d %b %Y'),
                        'refund_description': refund_transaction.refund_description,
                        'payment_id': payment.pg_paymentid,
                    }
                )

    return refunds


def write_refunds(filename, rows):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        fieldnames = [
            'transaction_id',
            'refund_description',
            'settlement_id',
            'refunded_at',
            'order_id',
            'order_date',
            'payment_id',
            'amount',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
