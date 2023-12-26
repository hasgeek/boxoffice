import requests

from . import app, rq
from baseframe import _


@rq.job('boxoffice')
def send_telegram_message(buyer_fullname, line_item_title):
    with app.test_request_context():
        message_text = _("{user} purchased {title}").format(
            user=buyer_fullname, title=line_item_title
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
