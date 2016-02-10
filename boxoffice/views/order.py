import json
import requests
from flask import url_for, request, jsonify
from flask.ext.cors import cross_origin
from coaster.views import load_models
from boxoffice import app
from boxoffice.models import db, Organization, Item, Inventory, User, LineItem
from boxoffice.models.order import Order, Payment, Transaction

ALLOWED_ORIGINS = ['http://shreyas-wlan.dev:8000']


@app.route('/<organization>/<inventory>/order', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (Inventory, {'name': 'inventory'}, 'inventory')
    )
@cross_origin(origins=ALLOWED_ORIGINS)
def order(organization, inventory):
    # change to get user
    user = User.query.first()
    order = Order(user=user, inventory=inventory)
    form_values = request.form.to_dict().keys()
    if form_values:
        form_values_json = json.loads(form_values[0])
        # user = User.find_or_create(email=form_values_json.get('email'), phone=form_values_json.get('phone'), name=form_values_json.get('name'))
        # order.user = user
        for line_item in form_values_json.get('line_items'):
            item = Item.get(order.inventory, line_item.get('name'))
            line_item = LineItem(item=item, order=order, quantity=line_item.get('quantity'))
            line_item.set_amounts()
        db.session.add(order)
        db.session.commit()
        return jsonify(code=200, order_id=order.id, payment_url=url_for('payment', order=order.id))


@app.route('/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@cross_origin(origins=ALLOWED_ORIGINS)
def payment(order):
    form_values = request.form.to_dict().keys()
    pg_payment_id = json.loads(form_values[0]).get('pg_payment_id')
    payment = Payment(pg_payment_id=pg_payment_id, order=order)
    order_amounts = order.calculate()
    url = 'https://api.razorpay.com/v1/payments/{pg_payment_id}/capture'.format(pg_payment_id=payment.pg_payment_id)
    # Razorpay requires the amount to be in paisa
    resp = requests.post(url, data={'amount': order_amounts.final_amount*100},
            auth=(app.config.get('RAZORPAY_KEY_ID'), app.config.get('RAZORPAY_KEY_SECRET')))

    if resp.status_code == 200:
        payment.capture()
        db.session.add(payment)
        transaction = Transaction(order=order, payment=payment, amount=order_amounts.final_amount)
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
    pass
    # render_template('invoice.html', order=order)
