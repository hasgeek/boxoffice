# -*- coding: utf-8 -*-

import datetime
import requests
from boxoffice import app, db
from boxoffice.models import Order, OnlinePayment, PaymentTransaction, TRANSACTION_TYPE, ORDER_STATUS
from boxoffice.models.payment import CURRENCY
from decimal import Decimal

base_url = 'https://api.razorpay.com/v1'


def get_refunds(paymentid):
    url = '{base_url}/payments/{paymentid}/refunds'.format(base_url=base_url, paymentid=paymentid)
    resp = requests.get(url, auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))
    return resp.json()


def amount_in_paise(amount):
    return int(amount * 100)


def amount_in_rupees(amount):
    return Decimal(amount / 100.0)


def epoch_dt(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()


def sync_refunds():
    epoch = datetime.datetime.utcfromtimestamp(0)
    payments = OnlinePayment.query.all()
    for payment in payments:
        rp_refunds = get_refunds(payment.pg_paymentid)
        used_pg_refundids = []
        for refund in payment.order.refund_transactions:
            if not refund.pg_refundid:
                refund_epoch_dt = (refund.created_at - epoch).total_seconds()
                possible_rp_refunds = [rp_refund
                    for rp_refund in rp_refunds['items']
                    if rp_refund['id'] not in used_pg_refundids
                    and amount_in_rupees(rp_refund['amount']) == refund.amount]
                correspongding_rp_refund = min(possible_rp_refunds,
                    key=lambda rp_refund: abs(rp_refund['created_at'] - refund_epoch_dt))
                if not correspongding_rp_refund or amount_in_paise(refund.amount) != correspongding_rp_refund['amount']:
                    raise "Oops! No refund found for {refundid}."
                refund.pg_refundid = correspongding_rp_refund['id']
                used_pg_refundids.append(correspongding_rp_refund['id'])
    db.session.commit()


def remove_duplicate_payments():
    orders = Order.query.all()
    for order in orders:
        payments = OnlinePayment.query.filter(OnlinePayment.order == order).all()
        if len(payments) > 1:
            dupes = []
            for payment in payments:
                if not payment.transactions:
                    dupes.append(payment)
            for dupe in dupes:
                db.session.delete(dupe)
    db.session.commit()


def get_duplicate_payments():
    orders = Order.query.filter(Order.status.in_(ORDER_STATUS.TRANSACTION)).all()
    dupes = []
    for order in orders:
        payments = OnlinePayment.query.filter(OnlinePayment.order == order).all()
        if len(payments) > 1:
            for payment in payments:
                if not payment.transactions:
                    dupes.append(payment)
    return dupes


def import_missing_refunds():
    payments = OnlinePayment.query.all()
    for payment in payments:
        rp_refunds = get_refunds(payment.pg_paymentid)
        if rp_refunds.get('items'):
            for rp_refund in rp_refunds['items']:
                refund = PaymentTransaction.query.filter_by(pg_refundid=rp_refund['id']).one_or_none()
                if not refund:
                    db.session.add(PaymentTransaction(
                        online_payment=payment,
                        order=payment.order,
                        amount=amount_in_rupees(rp_refund['amount']),
                        pg_refundid=rp_refund['id'],
                        created_at=datetime.datetime.utcfromtimestamp(rp_refund['created_at']),
                        refunded_at=datetime.datetime.utcfromtimestamp(rp_refund['created_at']),
                        transaction_type=TRANSACTION_TYPE.REFUND,
                        currency=CURRENCY.INR
                        ))
    db.session.commit()
