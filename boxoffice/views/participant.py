# -*- coding: utf-8 -*-

from flask import request, jsonify, make_response
from .. import app
from ..models import db
from ..models import LineItem, Assignee
from ..models import Order
from coaster.views import load_models
from utils import xhr_only


@app.route('/participant/<access_token>/assign', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Order, {'access_token': 'access_token'}, 'order')
    )
@xhr_only
def assign(order):
    """
    Assign a line_item to a participant
    """
    assignee_dict = request.json.get('attendee')
    if not request.json or not assignee_dict or not assignee_dict.get('email') or not assignee_dict.get('fullname'):
        return make_response(jsonify(message='Missing Attendee details'), 400)
    line_item = LineItem.query.get(request.json.get('line_item_id'))
    item_assignee_details = line_item.item.assignee_details
    assignee_details = {}
    for key in item_assignee_details.keys():
        assignee_details[key] = assignee_dict.get(key)
    if line_item.current_assignee and assignee_dict['email'] == line_item.current_assignee.email:
        # updating details of the current assignee
        line_item.current_assignee.fullname = assignee_dict['fullname']
        line_item.current_assignee.phone = assignee_dict['phone']
        line_item.current_assignee.details = assignee_details
    else:
        # change of assignee
        if line_item.current_assignee:
            # Archive current assignee
            line_item.current_assignee.current = None
        existing_assignee = Assignee.query.filter(Assignee.email == assignee_dict.get('email'), Assignee.line_item == line_item).first()
        if existing_assignee:
            # Line item transferred back to a previous assignee
            existing_assignee.current = True
            existing_assignee.fullname = assignee_dict['fullname']
            existing_assignee.phone = assignee_dict['phone']
            existing_assignee.details = assignee_details
        else:
            new_assignee = Assignee(current=True, email=assignee_dict.get('email'), fullname=assignee_dict.get('fullname'),
                phone=assignee_dict.get('phone'), details=assignee_details, line_item=line_item)
            db.session.add(new_assignee)
    db.session.commit()
    return make_response(jsonify(message="Ticket assigned"), 201)
