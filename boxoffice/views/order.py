from pytz import utc, timezone
from boxoffice import app
from flask import redirect, url_for, render_template, request, jsonify
from coaster.views import load_models, jsonp
from boxoffice.models import Order
from flask.ext.cors import cross_origin

ALLOWED_ORIGINS = ['http://shreyas-wlan.dev:4000']


@app.route('/purchase_order', methods=['OPTIONS', 'POST'])
@cross_origin(origins=ALLOWED_ORIGINS, methods=['GET', 'OPTIONS', 'POST'])
def make_purchase_order():
    # order = Order.get(order_id)
    # for line_item in request.form.line_items
        # line_item = LineItem(item_id=line_item.item_id, order=order, quantity=line_item.quantity)
        # line_item.discounted_amount = calculate_discounted_amount()
        # line_item.tax_amount = calculate_tax_amount()
        # order.line_items.append(line_item)
    # return jsonify(...)
    pass


@app.route('/sales_order', methods=['POST'])
def make_sales_order():
    pass


@app.route('/sales_order', methods=['POST'])
def invoice():
    pass
