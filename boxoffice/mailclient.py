# -*- coding: utf-8 -*-

from flask import render_template
from flask.ext.mail import Message
from html2text import html2text
from boxoffice.models import Order
from boxoffice import mail, app


def send_invoice_email(order_id, subject="Your Invoice"):
    """
    Sends an invoice with a PDF attached, to the order's buyer
    """
    with app.test_request_context():
        order = Order.query.get(order_id)
        line_items_dict = {}
        for line_item in order.line_items:
            line_items_dict.setdefault(line_item.item.id, []).append(line_item)
        msg = Message(subject=subject, recipients=[order.buyer_email])
        html = render_template('cash_receipt.html', order=order, line_items=line_items_dict)
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)
