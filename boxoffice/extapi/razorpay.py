import requests
from boxoffice import app


base_url = 'https://api.razorpay.com/v1/payments'

__all__ = ['capture_payment']


def capture_payment(payment_id, amount):
    """
    Attempts to capture the payment, from Razorpay
    """
    verify_https = False if app.config.get('VERIFY_RAZORPAY_HTTPS') is False else True
    url = '{base_url}/{payment_id}/capture'.format(base_url=base_url, payment_id=payment_id)
    # Razorpay requires the amount to be in paisa
    resp = requests.post(url, data={'amount': amount*100},
        auth=(app.config.get('RAZORPAY_KEY_ID'), app.config.get('RAZORPAY_KEY_SECRET')), verify=verify_https)
    return True if resp.status_code == 200 else False
