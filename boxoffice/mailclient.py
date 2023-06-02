from decimal import Decimal
from uuid import UUID

from flask import render_template
from flask_mail import Message
from html2text import html2text
from premailer import transform as email_transform

from baseframe import _, __
from coaster.sqlalchemy import MarkdownComposite

from . import app, mail, rq
from .models import CURRENCY_SYMBOL, LINE_ITEM_STATUS, Assignee, LineItem, Order


@rq.job('boxoffice')
def send_receipt_mail(
    order_id: UUID,
    subject: str = __("Thank you for your order!"),
    template: str = 'order_confirmation_mail.html.jinja2',
):
    """Send buyer a link to fill attendee details and get cash receipt."""
    with app.test_request_context():
        order = Order.query.get(order_id)
        msg = Message(
            subject=subject,
            recipients=[order.buyer_email],
            bcc=[order.organization.contact_email],
        )
        line_items = (
            LineItem.query.filter(
                LineItem.order == order, LineItem.status == LINE_ITEM_STATUS.CONFIRMED
            )
            .order_by(LineItem.line_item_seq.asc())
            .all()
        )
        html = email_transform(
            render_template(
                template,
                order=order,
                org=order.organization,
                line_items=line_items,
                base_url=app.config['BASE_URL'],
                currency_symbol=CURRENCY_SYMBOL['INR'],
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_participant_assignment_mail(
    order_id: UUID,
    menu_title: str,
    team_member: str,
    subject=__("Please tell us who's coming!"),
):
    with app.test_request_context():
        order = Order.query.get(order_id)
        msg = Message(
            subject=subject,
            recipients=[order.buyer_email],
            bcc=[order.organization.contact_email],
        )
        html = email_transform(
            render_template(
                'participant_assignment_mail.html.jinja2',
                base_url=app.config['BASE_URL'],
                order=order,
                org=order.organization,
                menu_title=menu_title,
                team_member=team_member,
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_line_item_cancellation_mail(
    line_item_id: UUID, refund_amount: Decimal, subject=__("Ticket Cancellation")
):
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        ticket_title = line_item.ticket.title
        order = line_item.order
        is_paid = line_item.final_amount > Decimal('0')
        msg = Message(
            subject=subject,
            recipients=[order.buyer_email],
            bcc=[order.organization.contact_email],
        )
        # Only INR is supported as of now
        html = email_transform(
            render_template(
                'line_item_cancellation_mail.html.jinja2',
                base_url=app.config['BASE_URL'],
                order=order,
                line_item=line_item,
                ticket_title=ticket_title,
                org=order.organization,
                is_paid=is_paid,
                refund_amount=refund_amount,
                currency_symbol=CURRENCY_SYMBOL['INR'],
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_order_refund_mail(
    order_id: UUID, refund_amount: Decimal, note_to_user: MarkdownComposite
):
    with app.test_request_context():
        order = Order.query.get(order_id)
        subject = _("{menu_title}: Refund for receipt no. {invoice_no}").format(
            menu_title=order.menu.title,
            invoice_no=order.invoice_no,
        )
        msg = Message(
            subject=subject,
            recipients=[order.buyer_email],
            bcc=[order.organization.contact_email],
        )
        # Only INR is supported as of now
        html = email_transform(
            render_template(
                'order_refund_mail.html.jinja2',
                base_url=app.config['BASE_URL'],
                order=order,
                org=order.organization,
                note_to_user=note_to_user.html,
                refund_amount=refund_amount,
                currency_symbol=CURRENCY_SYMBOL['INR'],
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_ticket_assignment_mail(line_item_id: UUID):
    """Send a confirmation email when ticket has been assigned."""
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        order = line_item.order
        subject = _("{title}: Here's your ticket").format(title=order.menu.title)
        msg = Message(
            subject=subject,
            recipients=[line_item.current_assignee.email],
            bcc=[order.buyer_email],
        )
        html = email_transform(
            render_template(
                'ticket_assignment_mail.html.jinja2',
                order=order,
                org=order.organization,
                line_item=line_item,
                base_url=app.config['BASE_URL'],
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_ticket_reassignment_mail(
    line_item_id: UUID, old_assignee_id: UUID, new_assignee_id: UUID
):
    """Send notice of reassignment of ticket."""
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        order = line_item.order
        old_assignee = Assignee.query.get(old_assignee_id)
        new_assignee = Assignee.query.get(new_assignee_id)

        subject = _("{title}: Your ticket has been transfered to someone else").format(
            title=order.menu.title
        )
        msg = Message(
            subject=subject, recipients=[old_assignee.email], bcc=[order.buyer_email]
        )
        html = email_transform(
            render_template(
                'ticket_reassignment_mail.html.jinja2',
                old_assignee=old_assignee,
                new_assignee=new_assignee,
                order=order,
                org=order.organization,
                line_item=line_item,
                base_url=app.config['BASE_URL'],
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)
