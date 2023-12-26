import requests

from . import app, rq
from baseframe import _

@rq.job('boxoffice')
def send_telegram_message(buyer_fullname, line_item_title):
    with app.test_request_context():
        message_text = _(f'{buyer_fullname} purchased {line_item_title}')
        send_text = f'https://api.telegram.org/bot{app.config["TELEGRAM_BOT_TOKEN"]}/sendMessage'
        params = {
            'chat_id': app.config['TELEGRAM_CHAT_ID'],
            'message_thread_id': app.config['TELEGRAM_MESSAGE_THREAD_ID'],
            'text': message_text,
        }
        requests.post(send_text, data=params, timeout=30)
