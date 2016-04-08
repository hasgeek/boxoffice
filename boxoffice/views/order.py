from datetime import datetime
from decimal import Decimal
from flask import url_for, request, jsonify, render_template, make_response
from rq import Queue
from redis import Redis
from coaster.views import load_models
from .. import app
from ..models import db
from ..models import ItemCollection, LineItem, Item, DiscountCoupon, DiscountPolicy
from ..models import Order, OnlinePayment, PaymentTransaction, User, CURRENCY
from ..extapi import razorpay
from ..forms import LineItemForm, BuyerForm
from custom_exceptions import APIError
from boxoffice.mailclient import send_receipt_email
from utils import xhr_only, cors

redis_connection = Redis()
boxofficeq = Queue('boxoffice', connection=redis_connection)


def jsonify_line_items(line_items):
    """
    Serializes and return line items in the format:
    {item_id: {'quantity': Y, 'final_amount': Z, 'discounted_amount': Z, 'discount_policy_ids': ['d1', 'd2']}}
    """
    items_json = dict()
    for line_item in line_items:
        if not items_json.get(unicode(line_item.item_id)):
            items_json[unicode(line_item.item_id)] = {'quantity': 0, 'final_amount': Decimal(0), 'discounted_amount': Decimal(0), 'discount_policy_ids': []}
        if not items_json[unicode(line_item.item_id)].get('final_amount'):
            items_json[unicode(line_item.item_id)]['final_amount'] = Decimal(0)
        items_json[unicode(line_item.item_id)]['final_amount'] += line_item.base_amount - line_item.discounted_amount
        items_json[unicode(line_item.item_id)]['discounted_amount'] += line_item.discounted_amount
        items_json[unicode(line_item.item_id)]['quantity'] += 1
        if line_item.discount_policy_id and line_item.discount_policy_id not in items_json[unicode(line_item.item_id)]['discount_policy_ids']:
            items_json[unicode(line_item.item_id)]['discount_policy_ids'].append(line_item.discount_policy_id)
    return items_json


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
        return make_response(jsonify(message='<Missing></Missing> line items'), 400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        return make_response(jsonify(message='Invalid line items'), 400)

    # Make line item splits and compute amounts and discounts
    line_items = LineItem.calculate([{'item_id': li_form.data.get('item_id')}
        for li_form in line_item_forms
        for _ in range(li_form.data.get('quantity'))], coupons=request.json.get('discount_coupons'))
    items_json = jsonify_line_items(line_items)
    order_final_amount = sum([values['final_amount'] for values in items_json.values()])
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

    buyer_form = BuyerForm.from_json(request.json.get('buyer'))
    # See comment in LineItemForm about CSRF
    buyer_form.csrf_enabled = False
    if not buyer_form.validate():
        return make_response(jsonify(message='Invalid buyer details'), 400)

    user = User.query.filter_by(email=buyer_form.email.data).first()
    order = Order(user=user,
        organization=item_collection.organization,
        item_collection=item_collection,
        buyer_email=buyer_form.email.data,
        buyer_fullname=buyer_form.fullname.data,
        buyer_phone=buyer_form.phone.data)

    line_item_tups = LineItem.calculate([{'item_id': li_form.data.get('item_id')}
        for li_form in line_item_forms
        for _ in range(li_form.data.get('quantity'))], coupons=request.json.get('discount_coupons'))

    for idx, line_item_tup in enumerate(line_item_tups):
        item = Item.query.get(line_item_tup.item_id)
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

    db.session.add(order)
    db.session.commit()
    return make_response(jsonify(order_id=order.id,
        order_access_token=order.access_token,
        payment_url=url_for('payment', order=order.id),
        free_order_url=url_for('free', order=order.id),
        final_amount=order.get_amounts().final_amount), 201)


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
    order_amounts = order.get_amounts()
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
        boxofficeq.enqueue(send_receipt_email, order.id)
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

    order_amounts = order.get_amounts()
    online_payment = OnlinePayment(pg_paymentid=request.json.get('pg_paymentid'), order=order)

    rp_resp = razorpay.capture_payment(online_payment.pg_paymentid, order_amounts.final_amount)
    if rp_resp.status_code == 200:
        online_payment.confirm()
        db.session.add(online_payment)
        # Only INR is supported as of now
        transaction = PaymentTransaction(order=order, online_payment=online_payment,
            amount=order_amounts.final_amount, currency=CURRENCY.INR)
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
        boxofficeq.enqueue(send_receipt_email, order.id)
        return make_response(jsonify(message="Payment verified"), 201)
    else:
        online_payment.fail()
        db.session.add(online_payment)
        db.session.commit()
        raise APIError("Online payment failed for order - {order}".format(order=order.id), 502)


@app.route('/order/<access_token>/receipt', methods=['GET'])
@load_models(
    (Order, {'access_token': 'access_token'}, 'order')
    )
def receipt(order):
    return render_template('cash_receipt.html', order=order, org=order.organization)
