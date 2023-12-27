import requests

from baseframe import _

from . import app, rq
from .models import Order


@rq.job('boxoffice')
def send_telegram_message(order_id):
    with app.test_request_context():
        order = Order.query.get(order_id)
        message_text = ""
        for line_item in order.line_items:
            message_text += _("{user} purchased {title}\n").format(
                user=order.buyer_fullname, title=line_item.item.title
            )
        send_text = (
            f'https://api.telegram.org/bot{app.config["TELEGRAM_APIKEY"]}/sendMessage'
        )
        params = {
            'chat_id': app.config['TELEGRAM_CHATID'],
            'message_thread_id': app.config.get['TELEGRAM_THREADID'],
            'text': message_text,
        }
        requests.post(send_text, data=params, timeout=30)
