import requests
from boxoffice import app


base_url = 'https://api.razorpay.com/v1/payments'


def capture_payment(payment_id, amount):
    # Razorpay requires the amount to be in paisa
    url = '{base_url}/{payment_id}/capture'\
        .format(base_url=base_url, payment_id=payment_id)
    # Razorpay requires the amount to be in paisa
    resp = requests.post(url, data={'amount': amount*100},
        auth=(app.config.get('RAZORPAY_KEY_ID'),
        app.config.get('RAZORPAY_KEY_SECRET')))
    return True if resp.status_code == 200 else False
