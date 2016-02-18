import datetime
from flask import url_for, request, jsonify, render_template, abort
from flask.ext.cors import cross_origin
from coaster.views import load_models
from boxoffice import app
from boxoffice.models import db, Organization, Item, ItemCollection, LineItem, Price
from boxoffice.models.order import Order, Payment, PaymentTransaction, User
from boxoffice.extapi import razorpay
from .helpers import find_or_create_user
from forms import LineItemForm, BuyerForm
from utils import xhr_or_abort

ALLOWED_ORIGINS = ['http://shreyas-wlan.dev:8000', 'http://rootconf.vidya.dev:8090']


def calculate_line_items(line_items_dicts):
    for line_item_dict in line_items_dicts:
        item = Item.query.get(line_item_dict.get('item_id'))
        amounts, discount_policies = LineItem.get_amounts_and_discounts(Price.current(item).amount, line_item_dict.get('quantity'), item.discount_policies)
        line_item_dict['base_amount'] = amounts.base_amount
        line_item_dict['discounted_amount'] = amounts.discounted_amount
        line_item_dict['final_amount'] = amounts.final_amount
        line_item_dict['discount_policies'] = discount_policies

    return line_items_dicts


@app.route('/<organization>/<item_collection>/order', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
@xhr_or_abort
@cross_origin(origins=ALLOWED_ORIGINS)
def order(organization, item_collection):
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        abort(400)

    buyer_form = BuyerForm.from_json(request.json.get('buyer'))

    if not buyer_form.validate():
        abort(400)
    user = User.query.filter_by(email=buyer_form.email.data).first()
    order = Order(user=user,
                  item_collection=item_collection,
                  buyer_email=buyer_form.email.data,
                  buyer_fullname=buyer_form.fullname.data,
                  buyer_phone=buyer_form.phone.data)

    # Get line items with calcuated base_amount, discounted_amount and final_amount
    for line_item_dict in calculate_line_items([li_form.data for li_form in line_item_forms]):
        line_item = LineItem(item=Item.query.get(line_item_dict.get('item_id')),
                             order=order,
                             quantity=line_item_dict.get('quantity'),
                             ordered_at=datetime.datetime.now(),
                             base_amount=line_item_dict.get('base_amount'),
                             discounted_amount=line_item_dict.get('discounted_amount'),
                             final_amount=line_item_dict.get('final_amount'))
        db.session.add(line_item)
    db.session.add(order)
    db.session.commit()
    return jsonify(code=200, order_id=order.id, order_access_token=order.access_token,
                   payment_url=url_for('payment', order=order.id),
                   final_amount=order.get_amounts().final_amount)

@app.route('/kharcha', methods=['GET', 'OPTIONS', 'POST'])
@xhr_or_abort
@cross_origin(origins=ALLOWED_ORIGINS)
def kharcha():
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        abort(400)
    return jsonify(line_items=calculate_line_items([li_form.data for li_form in line_item_forms]))


@app.route('/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@xhr_or_abort
@cross_origin(origins=ALLOWED_ORIGINS)
def payment(order):
    pg_payment_id = request.json.get('pg_payment_id')
    if not (request.json and pg_payment_id):
        abort(400)
    payment = Payment(pg_payment_id=pg_payment_id, order=order)
    order_amounts = order.get_amounts()

    if razorpay.capture_payment(payment.pg_payment_id, order_amounts.final_amount):
        payment.capture()
        db.session.add(payment)
        transaction = PaymentTransaction(order=order, payment=payment, amount=order_amounts.final_amount)
        db.session.add(transaction)
        order.invoice()
        db.session.add(order)
        db.session.commit()
        return jsonify(code=200)
    else:
        payment.fail()
        return abort(402)


@app.route('/<access_token>/invoice', methods=['GET'])
@load_models(
    (Order, {'access_token': 'access_token'}, 'order')
    )
@cross_origin(origins=app.config.get('ALLOWED_ORIGINS'))
def invoice(order):
    return render_template('invoice.html', order=order)
