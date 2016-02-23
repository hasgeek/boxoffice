# -*- coding: utf-8 -*-

import pdfkit
from flask import render_template
from flask.ext.mail import Message
from html2text import html2text
from boxoffice.models import Order
from boxoffice import mail, app


def send_invoice_email(order_id, subject="Your Invoice", filename="order_invoice"):
    """
    Sends an invoice with a PDF attached, to the order's buyer
    """
    with app.test_request_context():
        order = Order.query.get(order_id)
        msg = Message(subject=subject, recipients=[order.buyer_email])
        html = render_template('invoice.html', order=order)
        pdf_file = pdfkit.from_string(html, False)
        msg.body = html2text(html)

        if len(filename) > 4:
            if filename[-3:] != '.pdf':
                filename = filename + '.pdf'

        msg.attach(filename, 'application/pdf', pdf_file)
        mail.send(msg)
