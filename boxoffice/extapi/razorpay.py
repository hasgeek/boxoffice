# -*- coding: utf-8 -*-

import requests
from coaster.utils import LabeledEnum
from baseframe import __, localize_timezone
from boxoffice import app
from boxoffice.models import OnlinePayment, LINE_ITEM_STATUS, PaymentTransaction, TRANSACTION_TYPE


# Don't use a trailing slash
base_url = 'https://api.razorpay.com/v1/payments'

__all__ = ['RAZORPAY_PAYMENT_STATUS', 'capture_payment']


class RAZORPAY_PAYMENT_STATUS(LabeledEnum):
    """
    Reflects payment statuses as specified in
    https://docs.razorpay.com/docs/return-objects
    """
    CREATED = (0, __("Created"))
    AUTHORIZED = (1, __("Authorized"))
    CAPTURED = (2, __("Captured"))
    #: Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))


def capture_payment(paymentid, amount):
    """
    Attempts to capture the payment, from Razorpay
    """
    verify_https = False if app.config.get('VERIFY_RAZORPAY_HTTPS') is False else True
    url = '{base_url}/{paymentid}/capture'.format(base_url=base_url, paymentid=paymentid)
    # Razorpay requires the amount to be in paisa and of type integer
    resp = requests.post(url, data={'amount': int(amount * 100)},
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']), verify=verify_https)
    return resp


def refund_payment(paymentid, amount):
    """
    Sends a POST request to Razorpay, to initiate a refund
    """
    url = '{base_url}/{paymentid}/refund'.format(base_url=base_url, paymentid=paymentid)
    # Razorpay requires the amount to be in paisa and of type integer
    resp = requests.post(url, data={'amount': int(amount * 100)}, auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))
    return resp

def get_settlements(date_range):
    settlements_url = 'https://api.razorpay.com/v1/settlements/report/combined'
    settlement_resp = requests.get(settlements_url,
        params={'year': date_range['year'], 'month': date_range['month']},
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))
    return settlement_resp.json()


def get_settled_transactions(date_range):
    settled_transactions = get_settlements(date_range)
    headers = ['settlement_id', 'transaction_type', 'order_id', 'payment_id', 'refund_id', 'item_collection', 'description', 'base_amount', 'discounted_amount', 'final_amount', 'order_paid_amount', 'transaction_date', 'settled_at', 'razorpay_fees', 'order_amount', 'credit', 'debit', 'receivable_amount', 'settlement_amount', 'buyer_fullname']
    rows = []
    external_transaction_msg = u"Transaction external to Boxoffice. Credited directly to Razorpay?"
    
    for settled_transaction in settled_transactions:
        if settled_transaction['type'] == 'settlement':
          rows.append({
              'settlement_id': settled_transaction['entity_id'],
              'settlement_amount': settled_transaction['amount'],
              'settled_at': settled_transaction['settled_at']

          })  
        elif settled_transaction['type'] == 'payment':
            payment = OnlinePayment.query.filter_by(pg_paymentid=settled_transaction['entity_id']).one_or_none()
            if payment:
                order = payment.order
                rows.append({
                    'settlement_id': settled_transaction['settlement_id'],
                    'transaction_type': settled_transaction['type'],
                    'order_id': order.id,
                    'payment_id': settled_transaction['entity_id'],
                    'razorpay_fees': settled_transaction['fee'],
                    'transaction_date': localize_timezone(order.paid_at, 'Asia/Kolkata'),
                    'credit': settled_transaction['credit'],
                    'buyer_fullname': order.buyer_fullname,
                    'item_collection': order.item_collection.title
                })
                for line_item in order.get_initial_line_items:
                    # some line items are voided or cancelled
                    # how do you retrieve the line items that were created during the order was created?
                    rows.append([settled_transaction['settlement_id'], settled_transaction['entity_id'], order.id, order.item_collection.title, line_item.item.title, '-', line_item.final_amount, '-', '-', '-'])
            else:
                # Transaction outside of Boxoffice
                rows.append({
                    'settlement_id': settled_transaction['settlement_id'],
                    'payment_id': settled_transaction['entity_id'],
                    'credit': settled_transaction['credit'],
                    'description': external_transaction_msg
                })
        elif settled_transaction['type'] == 'refund':
            payment = OnlinePayment.query.filter_by(settled_transactionid=settled_transaction['payment_id']).one()
            refund = PaymentTransaction.query.filter(PaymentTransaction.online_payment == payment,
                PaymentTransaction.transaction_type == TRANSACTION_TYPE.REFUND,
                PaymentTransaction.settled_transactionid == settled_transaction['entity_id']
                ).one()
            order = refund.order
            rows.append({
                'settlement_id': settled_transaction['settlement_id'],
                'refund_id': settled_transaction['entity_id'],
                'payment_id': settled_transaction['payment_id'],
                'order_id': order.id,
                'razorpay_fees': settled_transaction['fee'],
                'debit': settled_transaction['debit'],
                'buyer_fullname': order.buyer_fullname,
                'description': refund.refund_description,
                'amount': refund.amount,
                'item_collection': order.item_collection.title
            })
    return (headers, rows)