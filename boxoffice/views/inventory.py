import json
import requests
from flask import url_for, render_template, request, jsonify
from flask.ext.cors import cross_origin
from coaster.views import load_models, jsonp
from boxoffice import app
from boxoffice.models import db, Organization, Item, Category, Inventory, Price, User
from boxoffice.models.order import Order, Payment, Transaction

ALLOWED_ORIGINS = ['http://shreyas-wlan.dev:8000']


def item_json(item):
    price = Price.current(item)
    if price:
        return {
            'name': item.name,
            'title': item.title,
            'id': item.id,
            'description': item.description,
            'quantity_available': item.quantity_available,
            'quantity_total': item.quantity_total,
            'category_id': item.category_id,
            'inventory_id': item.inventory_id,
            'price': Price.current(item).amount
        }


def category_json(category):
    return {
        'id': category.id,
        'title': category.title,
        'inventory_id': category.inventory_id,
        'items': [item_json(item) for item in category.items]
    }


@app.route('/boxoffice.js')
def boxofficejs():
    return render_template('boxoffice.js', base_url=app.config.get('BASE_URL'))


@app.route('/<organization>/<inventory>')
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (Inventory, {'name': 'inventory'}, 'inventory')
    )
def inventory(organization, inventory):
    return jsonp(**{
        'html': render_template('boxoffice.html'),
        'categories': [category_json(category) for category in inventory.categories]
        })


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
        order.calculate(form_values_json.get('line_items'))
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
    url = 'https://api.razorpay.com/v1/payments/{pg_payment_id}/capture'.format(pg_payment_id=payment.pg_payment_id)
    # Razorpay requires the amount to be in paisa
    resp = requests.post(url, data={'amount': payment.order.final_amount*100},
            auth=(app.config.get('RAZORPAY_KEY_ID'), app.config.get('RAZORPAY_KEY_SECRET')))

    if resp.status_code == 200:
        payment.capture()
        db.session.add(payment)
        transaction = Transaction(order=order, payment=payment, amount=order.final_amount)
        db.session.add(transaction)
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
@cross_origin(origins=ALLOWED_ORIGINS)
def invoice(order):
    pass
    # render_template('invoice.html', order=order)
