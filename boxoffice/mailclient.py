# -*- coding: utf-8 -*-

from decimal import Decimal
from flask import render_template
from flask.ext.rq import job
from flask.ext.mail import Message
from html2text import html2text
from premailer import transform as email_transform
from .models import Order, LineItem, LINE_ITEM_STATUS, CURRENCY_SYMBOL
from . import mail, app


@job('boxoffice')
def send_receipt_mail(order_id, subject="Thank you for your order!"):
    """
    Sends an link to fill attendee details and cash receipt to the order's buyer
    """
    with app.test_request_context():
        order = Order.query.get(order_id)
        msg = Message(subject=subject, recipients=[order.buyer_email], bcc=[order.organization.contact_email])
        line_items = LineItem.query.filter(LineItem.order == order, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).order_by("line_item_seq asc").all()
        html = email_transform(render_template('order_confirmation_mail.html', order=order, org=order.organization, line_items=line_items, base_url=app.config['BASE_URL']))
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@job('boxoffice')
def send_participant_assignment_mail(order_id, item_collection_title, team_member, subject="Please tell us who's coming!"):
    with app.test_request_context():
        order = Order.query.get(order_id)
        msg = Message(subject=subject, recipients=[order.buyer_email], bcc=[order.organization.contact_email])
        html = email_transform(render_template('participant_assignment_mail.html', base_url=app.config['BASE_URL'], order=order, org=order.organization, item_collection_title=item_collection_title, team_member=team_member))
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@job('boxoffice')
def send_line_item_cancellation_mail(line_item_id, subject="Ticket Cancellation"):
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        item_title = line_item.item.title
        order = line_item.order
        is_paid = line_item.final_amount > Decimal('0')
        msg = Message(subject=subject, recipients=[order.buyer_email], bcc=[order.organization.contact_email])
        # Only INR is supported as of now
        html = email_transform(render_template('line_item_cancellation_mail.html',
            base_url=app.config['BASE_URL'],
            order=order, line_item=line_item, item_title=item_title, org=order.organization, is_paid=is_paid,
            currency_symbol=CURRENCY_SYMBOL['INR']))
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@job('boxoffice')
def send_ticket_assignment_mail(line_item_id, past_assignee):
    """
    Sends a confirmation email once details are filled and ticket has been assigned.
    """
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        order = line_item.order
        subject = order.item_collection.title + ": Here's your ticket"
        if past_assignee:
          cc_list = [order.buyer_email, past_assignee]
        else:
          cc_list = [order.buyer_email]
        msg = Message(subject=subject, recipients=[line_item.current_assignee.email], cc=cc_list)
        html = email_transform(render_template('ticket_assignment_mail.html', order=order, org=order.organization, line_item=line_item, base_url=app.config['BASE_URL']))
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)
