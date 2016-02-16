import json
import requests
import datetime
from flask import url_for, request, jsonify, render_template
from flask.ext.cors import cross_origin
from coaster.views import load_models
from boxoffice import app
from boxoffice.models import db, Organization, Item, ItemCollection, User, LineItem, Price
from boxoffice.models.order import Order, Payment, PaymentTransaction
from boxoffice.extapi import razorpay
from .helpers import find_or_create_user

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
@cross_origin(origins=ALLOWED_ORIGINS)
def order(organization, item_collection):
    form_values = request.form.to_dict().keys()
    if form_values:
        form_values_json = json.loads(form_values[0])
        user = find_or_create_user(form_values_json.get('buyer').get('email'))
        order = Order(user=user,
                      item_collection=item_collection,
                      buyer_email=form_values_json.get('buyer').get('email'),
                      buyer_fullname=form_values_json.get('buyer').get('fullname'),
                      buyer_phone=form_values_json.get('buyer').get('phone'))
        line_item_dicts = calculate_line_items(form_values_json.get('line_items'))
        for line_item_dict in line_item_dicts:
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
        order_amounts = order.get_amounts()
        return jsonify(code=200, order_id=order.id,
                       payment_url=url_for('payment', order=order.id),
                       final_amount=order_amounts.final_amount)


@app.route('/kharcha', methods=['GET', 'OPTIONS', 'POST'])
@cross_origin(origins=ALLOWED_ORIGINS)
def kharcha():
    try:
        form_values = request.form.to_dict().keys()
        # import IPython; IPython.embed()
        if form_values:
            form_values_json = json.loads(form_values[0])
            return jsonify(line_items=calculate_line_items(form_values_json.get('line_items')))
    except Exception:
        return jsonify(status=400)
    else:
        return jsonify(status=401)


@app.route('/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@cross_origin(origins=ALLOWED_ORIGINS)
def payment(order):
    form_values = request.form.to_dict().keys()
    pg_payment_id = json.loads(form_values[0]).get('pg_payment_id')
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
        return jsonify(code=402)


@app.route('/<order>/cancel', methods=['POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@cross_origin(origins=ALLOWED_ORIGINS)
def cancel(order):
    # line_items_dict = [{id: '', quantity: 3, name: ''}, {id: '', quantity: 4, name: ''}]
    # for line_item_dict in line_items_dict:
    #     line_item = LineItem.get(line_item_dict.get('id'))
    #    if line_item_dict.get('quantity') == 0:
    #        line_item.cancel()
    #    elif line_item_dict('quantity') < line_item.quantity:
    #        line_item.cancel()
    #        new_line_item = LineItem(quantity=line_item_dict('quantity'), order=order, item=line_item.item)
    #        db.session.add(new_line_item)
    # db.session.commit()
    # render_template('invoice.html', order=order)
    pass


@app.route('/<order>/invoice', methods=['GET'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@cross_origin(origins=app.config.get('ALLOWED_ORIGINS'))
def invoice(order):
    return render_template('invoice.html', order=order)
