from flask import url_for, request, jsonify, render_template, make_response
from .. import app
from ..models import db
from ..models import ItemCollection, LineItem, Item, DiscountCoupon, DiscountPolicy, Assignee
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
    if not request.json or not request.json.get('attendee'):
        return make_response(jsonify(message='<Missing></Missing> Attendee details'), 400)
    assignee_dict = request.json.get('attendee')
    line_item_id = request.json.get('line_item_id')
    line_item = LineItem.query.get(request.json.get('line_item_id'))
    assignee = Assignee.query.filter_by(email=assignee_dict.get('email')).one_or_none()
    if not assignee:
      assignee = Assignee(email=assignee_dict.get('email'), fullname=assignee_dict.get('fullname'), phone=assignee_dict.get('phone'))
      db.session.add(assignee)
    line_item.assignee = assignee
    db.session.add(line_item)
    db.session.commit()
    return make_response(jsonify(message="Ticket assigned"), 201)
