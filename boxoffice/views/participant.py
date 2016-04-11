from flask import request, jsonify, make_response
from .. import app
from ..models import db
from ..models import LineItem, Assignee
from ..models import Order
from coaster.views import load_models
from utils import xhr_only


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
    line_item = LineItem.query.get(request.json.get('line_item_id'))
    item_assignee_details = line_item.item.assignee_details
    assignee_details = {}
    for key in item_assignee_details.keys():
        assignee_details[key] = assignee_dict.get(key)
    assignee = Assignee(current=True, email=assignee_dict.get('email'), fullname=assignee_dict.get('fullname'),
        phone=assignee_dict.get('phone'), details=assignee_details, line_item=line_item)
    db.session.add(assignee)
    db.session.commit()
    return make_response(jsonify(message="Ticket assigned"), 201)
