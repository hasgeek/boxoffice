from flask import url_for, request, jsonify, render_template, make_response
from .. import app
from ..models import db
from ..models import ItemCollection, LineItem, Item, DiscountCoupon, DiscountPolicy
from ..models import Order, OnlinePayment, PaymentTransaction, User, CURRENCY
from coaster.views import render_with, load_models
from utils import xhr_only, cors



@app.route('/participant/<order>/assign', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'id': 'order'}, 'order')
    )
@xhr_only
def assign(order):
    """
    Assign a line_item to a participant
    """
    print('assign')
    return make_response(jsonify(message="Ticket assigned"), 201)
