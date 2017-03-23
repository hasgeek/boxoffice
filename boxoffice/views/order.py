# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from flask import url_for, request, jsonify, render_template, make_response, abort
from coaster.views import render_with, load_models
from baseframe import _
from .. import app, lastuser
from ..models import db
from ..models import ItemCollection, LineItem, Item, DiscountCoupon, DiscountPolicy, OrderSession, Assignee, LINE_ITEM_STATUS
from ..models import Order, OnlinePayment, PaymentTransaction, User, CURRENCY, ORDER_STATUS
from ..models.payment import TRANSACTION_TYPE
from ..extapi import razorpay, RAZORPAY_PAYMENT_STATUS
from ..forms import LineItemForm, BuyerForm, OrderSessionForm, OrderRefundForm
from custom_exceptions import PaymentGatewayError
from boxoffice.mailclient import send_receipt_mail, send_line_item_cancellation_mail, send_order_refund_mail
from utils import xhr_only, cors, date_format


def jsonify_line_items(line_items):
    """
    Serializes and return line items in the format:
    {item_id: {'quantity': Y, 'final_amount': Z, 'discounted_amount': Z, 'discount_policy_ids': ['d1', 'd2']}}
    """
    items_json = dict()
    for line_item in line_items:
        item = Item.query.get(line_item.item_id)
        if not items_json.get(unicode(line_item.item_id)):
            items_json[unicode(line_item.item_id)] = {'is_available': item.is_available, 'quantity': 0, 'final_amount': Decimal(0), 'discounted_amount': Decimal(0), 'discount_policy_ids': []}
        if line_item.base_amount is not None:
            items_json[unicode(line_item.item_id)]['base_amount'] = line_item.base_amount
            items_json[unicode(line_item.item_id)]['final_amount'] += line_item.base_amount - line_item.discounted_amount
            items_json[unicode(line_item.item_id)]['discounted_amount'] += line_item.discounted_amount
        else:
            items_json[unicode(line_item.item_id)]['final_amount'] = None
            items_json[unicode(line_item.item_id)]['discounted_amount'] = None
        items_json[unicode(line_item.item_id)]['quantity'] += 1
        items_json[unicode(line_item.item_id)]['quantity_available'] = item.quantity_available
        if line_item.discount_policy_id and line_item.discount_policy_id not in items_json[unicode(line_item.item_id)]['discount_policy_ids']:
            items_json[unicode(line_item.item_id)]['discount_policy_ids'].append(line_item.discount_policy_id)
    return items_json


def jsonify_assignee(assignee):
    if assignee:
        return {
            'id': assignee.id,
            'fullname': assignee.fullname,
            'email': assignee.email,
            'phone': assignee.phone,
            'details': assignee.details
        }


def jsonify_order(data):
    order = data['order']
    line_items = []
    for line_item in order.line_items:
        line_items.append({
            'seq': line_item.line_item_seq,
            'id': line_item.id,
            'title': line_item.item.title,
            'description': line_item.item.description.text,
            'final_amount': line_item.final_amount,
            'assignee_details': line_item.item.assignee_details,
            'assignee': jsonify_assignee(line_item.current_assignee),
            'is_confirmed': line_item.is_confirmed,
            'is_cancelled': line_item.is_cancelled,
            'cancelled_at': date_format(line_item.cancelled_at) if line_item.cancelled_at else "",
        })
    return jsonify(order_id=order.id, access_token=order.access_token,
        item_collection_name=order.item_collection.description_text, buyer_name=order.buyer_fullname,
        buyer_email=order.buyer_email,
        buyer_phone=order.buyer_phone, line_items=line_items)


def sanitize_coupons(coupons):
    if not isinstance(coupons, list):
        return []
    # Remove falsy values and coerce the valid values into unicode
    return [unicode(coupon_code) for coupon_code in coupons if coupon_code]


@app.route('/order/kharcha', methods=['OPTIONS', 'POST'])
@xhr_only
@cors
def kharcha():
    """
    Accepts JSON containing an array of line_items, with the quantity and item_id set for each line_item.

    Returns JSON of line items in the format:
    {item_id: {'quantity': Y, 'final_amount': Z, 'discounted_amount': Z, 'discount_policy_ids': ['d1', 'd2']}}
    """
    if not request.json or not request.json.get('line_items'):
        return make_response(jsonify(message='Missing line items'), 400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        return make_response(jsonify(message='Invalid line items'), 400)

    # Make line item splits and compute amounts and discounts
    line_items = LineItem.calculate([{'item_id': li_form.data.get('item_id')}
        for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))], coupons=sanitize_coupons(request.json.get('discount_coupons')))
    items_json = jsonify_line_items(line_items)
    order_final_amount = sum([values['final_amount'] for values in items_json.values() if values['final_amount'] is not None])
    return jsonify(line_items=items_json, order={'final_amount': order_final_amount})


@app.route('/ic/<item_collection>/order',
           methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
@xhr_only
@cors
def order(item_collection):
    """
    Accepts JSON containing an array of line_items with the quantity and item_id
    set for each item, and a buyer hash containing `email`, `fullname` and `phone`.

    Creates a purchase order, and returns a JSON containing the final_amount, order id
    and the URL to be used to register a payment against the order.
    """
    if not request.json or not request.json.get('line_items'):
        return make_response(jsonify(message='Missing line items'), 400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        return make_response(jsonify(message='Invalid line items'), 400)
    # See comment in LineItemForm about CSRF
    buyer_form = BuyerForm.from_json(request.json.get('buyer'), meta={'csrf': False})
    if not buyer_form.validate():
        return make_response(jsonify(message='Invalid buyer details'), 400)

    invalid_quantity_error_msg = _(u'Selected quantity for ‘{item}’ is not available. Please edit the order and update the quantity')
    item_dicts = Item.get_availability([line_item_form.data.get('item_id') for line_item_form in line_item_forms])

    for line_item_form in line_item_forms:
        title_quantity_count = item_dicts.get(line_item_form.data.get('item_id'))
        if title_quantity_count:
            item_title, item_quantity_total, line_item_count = title_quantity_count
            if (line_item_count + line_item_form.data.get('quantity')) > item_quantity_total:
                return make_response(jsonify(error_type='order_calculation',
                    message=invalid_quantity_error_msg.format(item=item_title)), 400)
        else:
            item = Item.query.get(line_item_form.data.get('item_id'))
            if line_item_form.data.get('quantity') > item.quantity_total:
                return make_response(jsonify(error_type='order_calculation',
                    message=invalid_quantity_error_msg.format(item=item.title)), 400)

    user = User.query.filter_by(email=buyer_form.email.data).first()
    order = Order(user=user,
        organization=item_collection.organization,
        item_collection=item_collection,
        buyer_email=buyer_form.email.data,
        buyer_fullname=buyer_form.fullname.data,
        buyer_phone=buyer_form.phone.data)

    line_item_tups = LineItem.calculate([{'item_id': li_form.data.get('item_id')}
        for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))], coupons=sanitize_coupons(request.json.get('discount_coupons')))

    for idx, line_item_tup in enumerate(line_item_tups):
        item = Item.query.get(line_item_tup.item_id)
        if item.is_available:
            if line_item_tup.discount_policy_id:
                policy = DiscountPolicy.query.get(line_item_tup.discount_policy_id)
            else:
                policy = None
            if line_item_tup.discount_coupon_id:
                coupon = DiscountCoupon.query.get(line_item_tup.discount_coupon_id)
            else:
                coupon = None

            line_item = LineItem(order=order, item=item, discount_policy=policy,
                line_item_seq=idx+1,
                discount_coupon=coupon,
                ordered_at=datetime.utcnow(),
                base_amount=line_item_tup.base_amount,
                discounted_amount=line_item_tup.discounted_amount,
                final_amount=line_item_tup.base_amount-line_item_tup.discounted_amount)
            db.session.add(line_item)
        else:
            return make_response(jsonify(error_type='order_calculation',
                message=_(u'‘{item}’ is no longer available.').format(item=item.title)), 400)

    db.session.add(order)

    if request.json.get('order_session'):
        order_session_form = OrderSessionForm.from_json(request.json.get('order_session'), meta={'csrf': False})
        if order_session_form.validate():
            order_session = OrderSession(order=order)
            order_session_form.populate_obj(order_session)
            db.session.add(order_session)

    db.session.commit()

    return make_response(jsonify(order_id=order.id,
        order_access_token=order.access_token,
        payment_url=url_for('payment', order=order.id),
        free_order_url=url_for('free', order=order.id),
        final_amount=order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER).final_amount), 201)


@app.route('/order/<order>/free', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@xhr_only
@cors
def free(order):
    """
    Completes a order which has a final_amount of 0
    """
    order_amounts = order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER)
    if order_amounts.final_amount == 0:
        order.confirm_sale()
        db.session.add(order)
        db.session.commit()
        for line_item in order.line_items:
            line_item.confirm()
            db.session.add(line_item)
            if line_item.discount_coupon:
                line_item.discount_coupon.update_used_count()
                db.session.add(line_item.discount_coupon)
        db.session.commit()
        send_receipt_mail.delay(order.id)
        return make_response(jsonify(message="Free order confirmed"), 201)
    else:
        return make_response(jsonify(message='Free order confirmation failed'), 402)


@app.route('/order/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@xhr_only
@cors
def payment(order):
    """
    Accepts JSON containing `pg_paymentid`.

    Creates a payment object, attempts to 'capture' the payment from Razorpay,
    and returns a JSON containing the result of the operation.

    A successful capture results in a `payment_transaction` registered against the order.
    """
    if not request.json.get('pg_paymentid'):
        return make_response(jsonify(message='Missing payment id.'), 400)

    order_amounts = order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER)
    online_payment = OnlinePayment(pg_paymentid=request.json.get('pg_paymentid'), order=order)

    rp_resp = razorpay.capture_payment(online_payment.pg_paymentid, order_amounts.final_amount)
    if rp_resp.status_code == 200:
        online_payment.confirm()
        db.session.add(online_payment)
        # Only INR is supported as of now
        transaction = PaymentTransaction(order=order, online_payment=online_payment, amount=order_amounts.final_amount, currency=CURRENCY.INR)
        db.session.add(transaction)
        order.confirm_sale()
        db.session.add(order)
        db.session.commit()
        for line_item in order.line_items:
            line_item.confirm()
            db.session.add(line_item)
            if line_item.discount_coupon:
                line_item.discount_coupon.update_used_count()
                db.session.add(line_item.discount_coupon)
        db.session.commit()
        send_receipt_mail.delay(order.id)
        return make_response(jsonify(message="Payment verified"), 201)
    else:
        online_payment.fail()
        db.session.add(online_payment)
        db.session.commit()
        raise PaymentGatewayError("Online payment failed for order - {order} with the following details - {msg}".format(order=order.id,
            msg=rp_resp.content), 424, 'Your payment failed. Please try again or contact us at {email}.'.format(email=order.organization.contact_email))


@app.route('/order/<access_token>/receipt', methods=['GET'])
@load_models(
    (Order, {'access_token': 'access_token'}, 'order')
    )
def receipt(order):
    return render_template('cash_receipt.html', order=order, org=order.organization, line_items=order.line_items, order_confirmed_amount=order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).confirmed_amount)


@app.route('/order/<access_token>/ticket', methods=['GET', 'POST'])
@render_with({'text/html': 'order.html', 'application/json': jsonify_order}, json=True)
@load_models(
    (Order, {'access_token': 'access_token'}, 'order')
    )
def line_items(order):
    return dict(order=order, org=order.organization)


def jsonify_orders(orders):
    api_orders = []

    def format_assignee(line_item):
        if not line_item.current_assignee:
            return dict()
        assignee = {
            'fullname': line_item.current_assignee.fullname,
            'email': line_item.current_assignee.email,
            'phone': line_item.current_assignee.phone
        }

        for key in line_item.item.assignee_details:
            assignee[key] = line_item.current_assignee.details.get(key)
        return assignee

    for order in orders:
        order_dict = {'invoice_no': order.invoice_no, 'line_items': []}
        for line_item in order.line_items:
            order_dict['line_items'].append({
                'assignee': format_assignee(line_item),
                'line_item_seq': line_item.line_item_seq,
                'line_item_status': u"confirmed" if line_item.is_confirmed else u"cancelled",
                'item': {
                    'title': line_item.item.title
                }
            })
        api_orders.append(order_dict)
    return api_orders


def get_coupon_codes_from_line_items(line_items):
    coupon_ids = [line_item.discount_coupon.id for line_item in line_items if line_item.discount_coupon]
    if coupon_ids:
        coupons = DiscountCoupon.query.filter(DiscountCoupon.id.in_(coupon_ids)).options(db.load_only('code')).all()
    else:
        coupons = []
    return [coupon.code for coupon in coupons]


def regenerate_line_item(order, original_line_item, updated_line_item_tup, line_item_seq):
    """
    Marks the original line item as `void`, and returns a new line item object
    with the updated attributes
    """
    original_line_item.make_void()
    item = Item.query.get(updated_line_item_tup.item_id)
    if updated_line_item_tup.discount_policy_id:
        policy = DiscountPolicy.query.get(updated_line_item_tup.discount_policy_id)
    else:
        policy = None
    if updated_line_item_tup.discount_coupon_id:
        coupon = DiscountCoupon.query.get(updated_line_item_tup.discount_coupon_id)
    else:
        coupon = None

    return LineItem(order=order, item=item, discount_policy=policy,
        status=LINE_ITEM_STATUS.CONFIRMED,
        line_item_seq=line_item_seq,
        discount_coupon=coupon,
        ordered_at=datetime.utcnow(),
        base_amount=updated_line_item_tup.base_amount,
        discounted_amount=updated_line_item_tup.discounted_amount,
        final_amount=updated_line_item_tup.base_amount-updated_line_item_tup.discounted_amount)


def update_order_on_line_item_cancellation(order, pre_cancellation_line_items, cancelled_line_item):
    """Cancels the given line item and updates the order"""
    active_line_items = [pre_cancellation_line_item
        for pre_cancellation_line_item in pre_cancellation_line_items
        if pre_cancellation_line_item != cancelled_line_item]
    recalculated_line_item_tups = LineItem.calculate(active_line_items, recalculate=True,
        coupons=get_coupon_codes_from_line_items(active_line_items))

    last_line_item_seq = LineItem.get_max_seq(order)
    for idx, line_item_tup in enumerate(recalculated_line_item_tups, start=last_line_item_seq+1):
        # Fetch the line item object
        pre_cancellation_line_item = [pre_cancellation_line_item for pre_cancellation_line_item in pre_cancellation_line_items if pre_cancellation_line_item.id == line_item_tup.id][0]
        # Check if the line item's amount has changed post-cancellation
        if line_item_tup.final_amount != pre_cancellation_line_item.final_amount:
            # Amount has changed, void this line item and regenerate the line item
            updated_line_item = regenerate_line_item(order, pre_cancellation_line_item, line_item_tup, idx)
            db.session.add(updated_line_item)
            current_assignee = pre_cancellation_line_item.current_assignee
            if current_assignee:
                db.session.add(Assignee(current=True, email=current_assignee.email,
                    fullname=current_assignee.fullname,
                    phone=current_assignee.phone, details=current_assignee.details,
                    line_item=updated_line_item))
    return order


def process_line_item_cancellation(line_item):
    if not line_item.is_free:
        order = line_item.order
        if line_item.discount_policy:
            pre_cancellation_order_amount = order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).confirmed_amount
            pre_cancellation_line_items = order.get_confirmed_line_items
            line_item.cancel()
            updated_order = update_order_on_line_item_cancellation(order, pre_cancellation_line_items, line_item)
            post_cancellation_order_amount = updated_order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).confirmed_amount
            refund_amount = pre_cancellation_order_amount - post_cancellation_order_amount
        else:
            line_item.cancel()
            refund_amount = line_item.final_amount

        payment = OnlinePayment.query.filter_by(order=line_item.order, pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED).one()
        rp_resp = razorpay.refund_payment(payment.pg_paymentid, refund_amount)
        if rp_resp.status_code == 200:
            db.session.add(PaymentTransaction(order=order, transaction_type=TRANSACTION_TYPE.REFUND,
                online_payment=payment, amount=refund_amount, currency=CURRENCY.INR))
            db.session.commit()
        else:
            raise PaymentGatewayError("Cancellation failed for order - {order} with the following details - {msg}".format(order=order.id,
                msg=rp_resp.content), 424,
            'Refund failed. Please try again or write to us at {email}.'.format(email=line_item.order.organization.contact_email))
    else:
        # free line item
        refund_amount = Decimal(0)
        line_item.cancel()
        db.session.commit()
    return refund_amount


@app.route('/line_item/<line_item_id>/cancel', methods=['POST'])
@lastuser.requires_login
@load_models(
    (LineItem, {'id': 'line_item_id'}, 'line_item'),
    permission='org_admin'
    )
def cancel_line_item(line_item):
    if not line_item.is_cancellable():
        return make_response(jsonify(status='error', error='non_cancellable', error_description='This ticket is not cancellable'), 403)

    refund_amount = process_line_item_cancellation(line_item)
    send_line_item_cancellation_mail.delay(line_item.id, refund_amount)
    return make_response(jsonify(status='ok', result={'message': 'Ticket cancelled', 'cancelled_at': date_format(line_item.cancelled_at)}), 200)


def process_partial_refund_for_order(order, order_refund_dict):
    form = OrderRefundForm.from_json(order_refund_dict, meta={'csrf': False})
    if form.validate():
        requested_refund_amount = form.amount.data
        confirmed_total = order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).final_amount
        cancelled_total = order.get_amounts(LINE_ITEM_STATUS.CANCELLED).final_amount
        total_paid_amount = confirmed_total + cancelled_total
        total_refund_amount = sum([order_transaction.amount
            for order_transaction in order.get_refund_transactions()])

        if (total_refund_amount + requested_refund_amount) >= total_paid_amount:
            return make_response(jsonify(status='error', error='excess_partial_refund',
                error_description='Invalid refund amount, must be lesser than net amount paid for the order'), 403)

        payment = OnlinePayment.query.filter_by(order=order,
            pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED).one()
        rp_resp = razorpay.refund_payment(payment.pg_paymentid, requested_refund_amount)
        if rp_resp.status_code == 200:
            db.session.add(PaymentTransaction(order=order, transaction_type=TRANSACTION_TYPE.REFUND,
                online_payment=payment, amount=requested_refund_amount, currency=CURRENCY.INR))
            db.session.commit()
        else:
            raise PaymentGatewayError("Refund failed for order - {order} with the following details - {msg}".format(order=order.id,
                msg=rp_resp.content), 424,
            'Refund failed. Please try again or contact support at {email}.'.format(email=order.organization.contact_email))

        send_order_refund_mail.delay(order.id, form.amount.data)
        return make_response(jsonify(status='ok', result={'message': 'Refund processed for order'}), 200)
    else:
        return make_response(jsonify(status='error', error='invalid_input',
            error_description='Please enter a valid amount and currency'), 403)


@app.route('/order/<order_id>/partial_refund', methods=['POST'])
@lastuser.requires_login
@load_models(
    (Order, {'id': 'order_id'}, 'order'),
    permission='org_admin'
    )
def partial_refund_order(order):
    return process_partial_refund_for_order(order, request.json.get('order_refund'))


@app.route('/api/1/ic/<item_collection>/orders', methods=['GET', 'OPTIONS'])
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
def item_collection_orders(item_collection):
    organization = item_collection.organization
    # TODO: Replace with a better authentication system
    if not request.args.get('access_token') or request.args.get('access_token') != organization.details.get("access_token"):
        abort(401)
    orders = item_collection.orders.filter(Order.status.in_([ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE])).all()
    return jsonify(orders=jsonify_orders(orders))
