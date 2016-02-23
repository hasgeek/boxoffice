from datetime import datetime
from flask import url_for, request, jsonify, render_template, abort
from flask.ext.cors import cross_origin
from rq import Queue
from redis import Redis
from coaster.views import load_models
from boxoffice import app, ALLOWED_ORIGINS
from boxoffice.models import db, Organization, Item
from boxoffice.models import ItemCollection, LineItem
from boxoffice.models.order import Order, OnlinePayment, PaymentTransaction, User
from boxoffice.extapi import razorpay
from forms import LineItemForm, BuyerForm
from boxoffice.mailclient import send_invoice_email
from utils import xhr_only, api_result

redis_connection = Redis()
boxofficeq = Queue('boxoffice', connection=redis_connection)


@app.route('/kharcha', methods=['OPTIONS', 'POST'])
@xhr_only
@cross_origin(origins=ALLOWED_ORIGINS)
def kharcha():
    """
    Accepts JSON containing an array of line_items, with the quantity and item_id set for each line_item.

    Returns JSON, containing an array of line_items with the base_amount, discounted_amount, final_amount
    and discount_policies set for each line item.
    """
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        api_result(400, 'invalid_line_items')
    line_item_dicts = LineItem.populate_amounts_and_discounts([li_form.data for li_form in line_item_forms])
    return jsonify(line_items=line_item_dicts)


@app.route('/<organization>/<item_collection>/order',
           methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Organization, {'name': 'organization'}, 'organization'),
    (ItemCollection, {'name': 'item_collection'}, 'item_collection')
    )
@xhr_only
@cross_origin(origins=ALLOWED_ORIGINS)
def order(organization, item_collection):
    """
    Accepts JSON containing an array of line_items with the quantity and item_id
    set for each item, and a buyer hash containing `email`, `fullname` and `phone`.

    Creates a purchase order, and returns a JSON containing the final_amount, order id
    and the URL to be used to register a payment against the order.
    """
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        api_result(400, 'invalid_line_items')

    buyer_form = BuyerForm.from_json(request.json.get('buyer'))

    if not buyer_form.validate():
        api_result(400, 'invalid_buyer')

    user = User.query.filter_by(email=buyer_form.email.data).first()
    order = Order(user=user,
        item_collection=item_collection,
        buyer_email=buyer_form.email.data,
        buyer_fullname=buyer_form.fullname.data,
        buyer_phone=buyer_form.phone.data)

    line_item_dicts = LineItem.populate_amounts_and_discounts([li_form.data for li_form in line_item_forms])
    for line_item_dict in line_item_dicts:
        line_item = LineItem(item=Item.query.get(line_item_dict.get('item_id')),
            order=order,
            quantity=line_item_dict.get('quantity'),
            ordered_at=datetime.utcnow(),
            base_amount=line_item_dict.get('base_amount'),
            discounted_amount=line_item_dict.get('discounted_amount'),
            final_amount=line_item_dict.get('final_amount'))
        db.session.add(line_item)
    db.session.add(order)
    db.session.commit()
    return jsonify(code=200, order_id=order.id,
        order_access_token=order.access_token,
        order_hash=order.order_hash,
        payment_url=url_for('payment', order=order.id),
        final_amount=order.get_amounts().final_amount)


@app.route('/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@xhr_only
@cross_origin(origins=ALLOWED_ORIGINS)
def payment(order):
    """
    Accepts JSON containing `pg_payment_id`.

    Creates a payment object, attempts to 'capture' the payment from Razorpay,
    and returns a JSON containing the result of the operation.

    A successful capture results in a `payment_transaction` registered against the order.
    """
    pg_payment_id = request.json.get('pg_payment_id')
    if not (request.json and pg_payment_id):
        abort(400)

    order_amounts = order.get_amounts()
    online_payment = OnlinePayment(pg_payment_id=pg_payment_id, order=order)

    rp_resp = razorpay.capture_payment(online_payment.pg_payment_id, order_amounts.final_amount)
    if rp_resp:
        online_payment.confirm()
        db.session.add(online_payment)
        transaction = PaymentTransaction(order=order, online_payment=online_payment, amount=order_amounts.final_amount)
        db.session.add(transaction)
        order.confirm_sale()
        db.session.add(order)
        db.session.commit()
        boxofficeq.enqueue(send_invoice_email, order.id)
        return jsonify(code=200)
    else:
        online_payment.fail()
        db.session.commit()
        #raise an exception and return user readable error msg.
        #Also send a mail to the user with order details
        return api_result(402, 'payment_capture_failed')


@app.route('/<access_token>/invoice', methods=['GET'])
@load_models(
    (Order, {'access_token': 'access_token'}, 'order')
    )
def invoice(order):
    return render_template('invoice.html', order=order)
