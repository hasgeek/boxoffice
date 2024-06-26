from decimal import Decimal
from uuid import UUID

from flask import render_template
from flask_mail import Message
from html2text import html2text
from premailer import transform as email_transform

from baseframe import _
from coaster.sqlalchemy import MarkdownComposite

from . import app, mail, rq
from .models import Assignee, CurrencySymbol, LineItem, LineItemStatus, Order


@rq.job('boxoffice')
def send_receipt_mail(
    order_id: UUID,
    subject: str | None = None,
    template: str = 'order_confirmation_mail.html.jinja2',
) -> None:
    """Send buyer a link to fill attendee details and get cash receipt."""
    with app.test_request_context():
        if subject is None:
            subject = _("Thank you for your order!")
        order = Order.query.get(order_id)
        if order is None:
            err = f"Unable to find Order with id={order_id!r}"
            raise ValueError(err)
        msg = Message(
            subject=subject,
            recipients=[order.buyer_email],
            bcc=[order.organization.contact_email],
        )
        line_items = (
            LineItem.query.filter(
                LineItem.order == order, LineItem.status == LineItemStatus.CONFIRMED
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
                currency_symbol=CurrencySymbol.INR,
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
    subject: str | None = None,
) -> None:
    with app.test_request_context():
        if subject is None:
            subject = _("Please tell us who's coming!")
        order = Order.query.get(order_id)
        if order is None:
            err = f"Unable to find Order with id={order_id!r}"
            raise ValueError(err)
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
    line_item_id: UUID, refund_amount: Decimal, subject: str | None = None
) -> None:
    with app.test_request_context():
        if subject is None:
            subject = _("Ticket Cancellation")
        line_item = LineItem.query.get(line_item_id)
        if line_item is None:
            err = f"Unable to find LineItem with id={line_item_id!r}"
            raise ValueError(err)
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
                currency_symbol=CurrencySymbol.INR,
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_order_refund_mail(
    order_id: UUID, refund_amount: Decimal, note_to_user: MarkdownComposite
) -> None:
    with app.test_request_context():
        order = Order.query.get(order_id)
        if order is None:
            err = f"Unable to find Order with id={order_id!r}"
            raise ValueError(err)
        subject = _("{menu_title}: Refund for receipt no. {receipt_no}").format(
            menu_title=order.menu.title,
            receipt_no=order.receipt_no,
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
                currency_symbol=CurrencySymbol.INR,
            )
        )
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)


@rq.job('boxoffice')
def send_ticket_assignment_mail(line_item_id: UUID) -> None:
    """Send a confirmation email when ticket has been assigned."""
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        if line_item is None:
            err = f"Unable to find LineItem with id={line_item_id!r}"
            raise ValueError(err)
        if line_item.assignee is None:
            err = f"LineItem.assignee is None for LineItem.id={line_item_id!r}"
            raise ValueError(err)
        order = line_item.order
        subject = _("{title}: Here's your ticket").format(title=order.menu.title)
        msg = Message(
            subject=subject,
            recipients=[line_item.assignee.email],
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
) -> None:
    """Send notice of reassignment of ticket."""
    with app.test_request_context():
        line_item = LineItem.query.get(line_item_id)
        old_assignee = Assignee.query.get(old_assignee_id)
        new_assignee = Assignee.query.get(new_assignee_id)
        if line_item is None or old_assignee is None or new_assignee is None:
            err = (
                f"Unexpected None value in line_item={line_item!r},"
                f" old_assignee={old_assignee!r}, new_assignee={new_assignee!r}"
            )
            raise ValueError(err)
        order = line_item.order

        subject = _("{title}: Your ticket has been transferred to someone else").format(
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
