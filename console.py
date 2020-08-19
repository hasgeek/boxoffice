# -*- coding: utf-8 -*-
import csv
import datetime
import logging
from collections import OrderedDict
from decimal import Decimal

from flask import jsonify, make_response

import IPython
from boxoffice import app
from boxoffice.extapi import razorpay
from boxoffice.mailclient import send_participant_assignment_mail, send_receipt_mail
from boxoffice.models import (
    CURRENCY,
    INVOICE_STATUS,
    LINE_ITEM_STATUS,
    ORDER_STATUS,
    Invoice,
    ItemCollection,
    OnlinePayment,
    Order,
    Organization,
    PaymentTransaction,
    db,
)
from boxoffice.views.custom_exceptions import PaymentGatewayError
from boxoffice.views.order import process_partial_refund_for_order
from isoweek import Week

from coaster.utils import isoweek_datetime, midnight_to_utc, utcnow

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def sales_by_date(sales_datetime, item_ids, user_tz):
    """
    Returns the sales amount accrued during the day for a given date/datetime,
    list of item_ids and timezone.
    """
    if not item_ids:
        return None

    start_at = midnight_to_utc(sales_datetime, timezone=user_tz)
    end_at = midnight_to_utc(
        sales_datetime + datetime.timedelta(days=1), timezone=user_tz
    )
    sales_on_date = (
        db.session.query('sum')
        .from_statement(
            db.text(
                '''SELECT SUM(final_amount) FROM line_item
        WHERE status=:status AND ordered_at >= :start_at AND ordered_at < :end_at
        AND line_item.item_id IN :item_ids
        '''
            )
        )
        .params(
            status=LINE_ITEM_STATUS.CONFIRMED,
            start_at=start_at,
            end_at=end_at,
            item_ids=tuple(item_ids),
        )
        .scalar()
    )
    return sales_on_date if sales_on_date else Decimal(0)


def calculate_weekly_sales(item_collection_ids, user_tz, year):
    """
    Calculates sales per week for items in the given set of item_collection_ids in a given year,
    in the user's timezone.
    """
    ordered_week_sales = OrderedDict()
    for year_week in Week.weeks_of_year(year):
        ordered_week_sales[year_week.week] = 0
    start_at = isoweek_datetime(year, 1, user_tz)
    end_at = isoweek_datetime(year + 1, 1, user_tz)

    week_sales = (
        db.session.query('sales_week', 'sum')
        .from_statement(
            db.text(
                '''
        SELECT EXTRACT(WEEK FROM ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)
        AS sales_week, SUM(final_amount) AS sum
        FROM line_item INNER JOIN item on line_item.item_id = item.id
        WHERE status IN :statuses AND item_collection_id IN :item_collection_ids
        AND ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone >= :start_at
        AND ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone < :end_at
        GROUP BY sales_week ORDER BY sales_week;
        '''
            )
        )
        .params(
            timezone=user_tz,
            statuses=tuple([LINE_ITEM_STATUS.CONFIRMED, LINE_ITEM_STATUS.CANCELLED]),
            start_at=start_at,
            end_at=end_at,
            item_collection_ids=tuple(item_collection_ids),
        )
        .all()
    )

    for week_sale in week_sales:
        ordered_week_sales[int(week_sale.sales_week)] = week_sale.sum

    return ordered_week_sales


def sales_delta(user_tz, item_ids):
    """Calculates the percentage difference in sales between today and yesterday"""
    today = utcnow().date()
    yesterday = today - datetime.timedelta(days=1)
    today_sales = sales_by_date(today, item_ids, user_tz)
    yesterday_sales = sales_by_date(yesterday, item_ids, user_tz)
    if not today_sales or not yesterday_sales:
        return 0
    return round(Decimal('100') * (today_sales - yesterday_sales) / yesterday_sales, 2)


def process_payment(order_id, pg_paymentid):
    order = Order.query.get(order_id)
    order_amounts = order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER)

    online_payment = OnlinePayment.query.filter_by(
        pg_paymentid=pg_paymentid,
        order=order
    ).first()
    if online_payment is None:
        online_payment = OnlinePayment(pg_paymentid=pg_paymentid, order=order)

    rp_resp = razorpay.capture_payment(
        online_payment.pg_paymentid, order_amounts.final_amount
    )
    if rp_resp.status_code == 200:
        online_payment.confirm()
        db.session.add(online_payment)
        # Only INR is supported as of now
        transaction = PaymentTransaction(
            order=order,
            online_payment=online_payment,
            amount=order_amounts.final_amount,
            currency=CURRENCY.INR,
        )
        db.session.add(transaction)
        order.confirm_sale()
        db.session.add(order)
        invoice_organization = order.organization.invoicer if order.organization.invoicer else order.organization
        invoice = Invoice(order=order, organization=invoice_organization)
        db.session.add(invoice)
        db.session.commit()
        for line_item in order.line_items:
            line_item.confirm()
            db.session.add(line_item)
            if line_item.discount_coupon:
                line_item.discount_coupon.update_used_count()
                db.session.add(line_item.discount_coupon)
        db.session.commit()
        with app.test_request_context():
            send_receipt_mail.queue(order.id)
            return make_response(jsonify(message="Payment verified"), 201)
    else:
        online_payment.fail()
        db.session.add(online_payment)
        db.session.commit()
        raise PaymentGatewayError(
            "Online payment failed for order - {order} with the following details - {msg}".format(
                order=order.id, msg=rp_resp.content
            ),
            424,
            'Your payment failed. Please try again or contact us at {email}.'.format(
                email=order.organization.contact_email
            ),
        )


def reprocess_successful_payment(order_id):
    order = Order.query.get(order_id)
    if not order.is_confirmed:
        order_amounts = order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER)
        online_payment = order.online_payments[0]
        online_payment.confirm()
        db.session.add(online_payment)
        # Only INR is supported as of now
        transaction = PaymentTransaction(
            order=order,
            online_payment=online_payment,
            amount=order_amounts.final_amount,
            currency=CURRENCY.INR,
        )
        db.session.add(transaction)
        order.confirm_sale()
        db.session.add(order)
        invoice_organization = order.organization.invoicer if order.organization.invoicer else order.organization
        invoice = Invoice(order=order, organization=invoice_organization)
        db.session.add(invoice)
        db.session.commit()
        for line_item in order.line_items:
            line_item.confirm()
            db.session.add(line_item)
            if line_item.discount_coupon:
                line_item.discount_coupon.update_used_count()
                db.session.add(line_item.discount_coupon)
        db.session.commit()
        with app.test_request_context():
            send_receipt_mail.queue(order.id)
            return make_response(jsonify(message="Payment verified"), 201)


def make_invoice_nos():
    orgs = Organization.query.all()
    for org in orgs:
        for order in Order.query.filter(
            Order.organization == org, Order.paid_at >= '2017-06-30 18:30'
        ).all():
            if (
                order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).final_amount
                or order.get_amounts(LINE_ITEM_STATUS.CANCELLED).final_amount
            ):
                db.session.add(Invoice(order=order, organization=org))
    db.session.commit()


def partial_refund(**kwargs):
    """
    Processes a partial refund for an order.
    Params are order_id, amount, internal_note, refund_description, note_to_user
    """
    form_dict = {
        'amount': kwargs['amount'],
        'internal_note': kwargs['internal_note'],
        'refund_description': kwargs['refund_description'],
        'note_to_user': kwargs['note_to_user'],
    }
    order = Order.query.get(kwargs['order_id'])

    with app.test_request_context():
        process_partial_refund_for_order(order, form_dict)


def finalize_invoices(org_name, start_at, end_at):
    org = Organization.query.filter_by(name=org_name).one()
    invoices = Invoice.query.filter(
        Invoice.organization == org,
        Invoice.created_at >= start_at,
        Invoice.created_at < end_at,
    ).all()
    for inv in invoices:
        inv.status = INVOICE_STATUS.FINAL
    db.session.commit()


def resend_attendee_details_email(
    item_collection_id, item_collection_title="", sender_team_member_name="Team Hasgeek"
):
    ic = ItemCollection.query.get(item_collection_id)
    headers, rows = ic.fetch_all_details()
    attendee_name_index = headers.index('attendee_fullname')
    order_id_index = headers.index('order_id')
    unfilled_orders = set()
    for order_row in rows:
        if not order_row[attendee_name_index]:
            unfilled_orders.add(order_row[order_id_index])

    for order_id in unfilled_orders:
        send_participant_assignment_mail(
            str(order_id), item_collection_title or ic.title, sender_team_member_name
        )


def order_report(org_name):
    org = Organization.query.filter_by(name=org_name).first()

    with open('order_report.csv', 'wb') as csvfile:
        order_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        order_writer.writerow(
            [
                "access_token",
                "paid_at",
                "invoiced_at",
                "status",
                "buyer_email",
                "buyer_fullname",
                "buyer_phone",
                "invoice_no",
                "net_amount",
            ]
        )

        for order in org.orders:
            if order.is_confirmed:
                order_writer.writerow(
                    [
                        order.access_token,
                        order.paid_at,
                        order.invoiced_at,
                        ORDER_STATUS[order.status],
                        order.buyer_email,
                        order.buyer_fullname.encode('utf-8'),
                        order.buyer_phone,
                        order.invoice_no,
                        order.net_amount,
                    ]
                )


IPython.embed()
