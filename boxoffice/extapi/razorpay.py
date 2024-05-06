from datetime import tzinfo
from decimal import Decimal
from typing import Any, TypedDict

import requests

from baseframe import localize_timezone

from .. import app
from ..models import OnlinePayment, PaymentTransaction, TransactionTypeEnum

# Don't use a trailing slash
base_url = 'https://api.razorpay.com/v1'


class YearMonth(TypedDict):
    year: int
    month: int


def capture_payment(paymentid: str, amount: Decimal) -> requests.Response:
    """Attempt to capture the payment from Razorpay."""
    verify_https = app.config.get('VERIFY_RAZORPAY_HTTPS', True)
    url = f'{base_url}/payments/{paymentid}/capture'
    # Razorpay requires the amount to be in paisa and of type integer
    return requests.post(
        url,
        data={'amount': int(amount * 100)},
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']),
        verify=verify_https,
        timeout=30,
    )


def refund_payment(paymentid: str, amount: Decimal) -> requests.Response:
    """Send a POST request to Razorpay to initiate a refund."""
    url = f'{base_url}/payments/{paymentid}/refund'
    # Razorpay requires the amount to be in paisa and of type integer
    return requests.post(
        url,
        data={'amount': int(amount * 100)},
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']),
        timeout=30,
    )


def get_settlements(date_range: YearMonth) -> Any:
    url = f'{base_url}/settlements/recon/combined'
    resp = requests.get(
        url,
        params={'year': date_range['year'], 'month': date_range['month']},
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']),
        timeout=30,
    )
    return resp.json()


def get_settled_transactions(
    date_range: YearMonth, tz: str | tzinfo | None = None
) -> tuple[list[str], list]:
    if not tz:
        tz = app.config['TIMEZONE']
    settled_transactions = get_settlements(date_range)
    headers = [
        'settlement_id',
        'transaction_type',
        'order_id',
        'payment_id',
        'refund_id',
        'menu',
        'description',
        'base_amount',
        'discounted_amount',
        'final_amount',
        'order_paid_amount',
        'transaction_date',
        'settled_at',
        'razorpay_fees',
        'order_amount',
        'credit',
        'debit',
        'receivable_amount',
        'settlement_amount',
        'buyer_fullname',
    ]
    # Nested list of dictionaries consisting of transaction details
    rows = []
    external_transaction_msg = (
        "Transaction external to Boxoffice. Credited directly to Razorpay?"
    )

    for settled_transaction in settled_transactions['items']:
        if settled_transaction['type'] == 'settlement':
            rows.append(
                {
                    'settlement_id': settled_transaction['entity_id'],
                    'settlement_amount': settled_transaction['amount'] / 100,
                    'settled_at': settled_transaction['settled_at'],
                    'transaction_type': settled_transaction['type'],
                }
            )
        elif settled_transaction['type'] == 'payment':
            payment = OnlinePayment.query.filter_by(
                pg_paymentid=settled_transaction['entity_id']
            ).one_or_none()
            if payment:
                order = payment.order
                assert order.paid_at is not None  # noqa: S101  # nosec B101
                rows.append(
                    {
                        'settlement_id': settled_transaction['settlement_id'],
                        'transaction_type': settled_transaction['type'],
                        'order_id': order.id,
                        'payment_id': settled_transaction['entity_id'],
                        'razorpay_fees': settled_transaction['fee'] / 100,
                        'transaction_date': localize_timezone(order.paid_at, tz),
                        'credit': settled_transaction['credit'] / 100,
                        'buyer_fullname': order.buyer_fullname,
                        'menu': order.menu.title,
                    }
                )
                for line_item in order.initial_line_items:
                    rows.append(
                        {
                            'settlement_id': settled_transaction['settlement_id'],
                            'payment_id': settled_transaction['entity_id'],
                            'order_id': order.id,
                            'menu': order.menu.title,
                            'description': line_item.ticket.title,
                            'base_amount': line_item.base_amount,
                            'discounted_amount': line_item.discounted_amount,
                            'final_amount': line_item.final_amount,
                        }
                    )
            else:
                # Transaction outside of Boxoffice
                rows.append(
                    {
                        'settlement_id': settled_transaction['settlement_id'],
                        'payment_id': settled_transaction['entity_id'],
                        'credit': settled_transaction['credit'] / 100,
                        'description': external_transaction_msg,
                    }
                )
        elif settled_transaction['type'] == 'refund':
            payment = OnlinePayment.query.filter_by(
                pg_paymentid=settled_transaction['payment_id']
            ).one()
            refund = PaymentTransaction.query.filter(
                PaymentTransaction.online_payment == payment,
                PaymentTransaction.transaction_type == TransactionTypeEnum.REFUND,
                PaymentTransaction.pg_refundid == settled_transaction['entity_id'],
            ).one()
            order = refund.order
            rows.append(
                {
                    'settlement_id': settled_transaction['settlement_id'],
                    'refund_id': settled_transaction['entity_id'],
                    'payment_id': settled_transaction['payment_id'],
                    'transaction_type': settled_transaction['type'],
                    'order_id': order.id,
                    'razorpay_fees': settled_transaction['fee'] / 100,
                    'debit': settled_transaction['debit'] / 100,
                    'buyer_fullname': order.buyer_fullname,
                    'description': refund.refund_description,
                    'amount': refund.amount / 100,
                    'menu': order.menu.title,
                }
            )
    return (headers, rows)
