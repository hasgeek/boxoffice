# -*- coding: utf-8 -*-

import requests
from coaster.utils import LabeledEnum
from baseframe import __
from boxoffice import app

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
    # Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))


def capture_payment(paymentid, amount):
    """
    Attempts to capture the payment, from Razorpay
    """
    verify_https = False if app.config.get('VERIFY_RAZORPAY_HTTPS') is False else True
    url = '{base_url}/{paymentid}/capture'.format(base_url=base_url, paymentid=paymentid)
    # Razorpay requires the amount to be in paisa
    resp = requests.post(url, data={'amount': amount*100},
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']), verify=verify_https)
    return resp


def refund_payment(paymentid, amount):
    """
    Sends a POST request to Razorpay, to initiate a refund
    """
    url = '{base_url}/{paymentid}/refund'.format(base_url=base_url, paymentid=paymentid)
    resp = requests.post(url, data={'amount': amount*100}, auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))
    return resp
