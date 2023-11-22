import requests

from . import app, rq


@rq.job('boxoffice')
def send_telegram_message(order):
    with app.test_request_context():
        message_text = f'{order.buyer_fullname} purchased {order.line_item.item.title}'
        send_text = f'https://api.telegram.org/bot{app.config["TELEGRAM_BOT_TOKEN"]}/sendMessage'
        params = {'chat_id': app.config["TELEGRAM_CHAT_ID"], 'text': message_text}
        requests.post(send_text, data=params, timeout=30)
