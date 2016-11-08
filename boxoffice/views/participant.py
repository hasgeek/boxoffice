# -*- coding: utf-8 -*-

from flask import request, jsonify, make_response
from .. import app
from ..models import db
from ..models import LineItem, Assignee
from ..models import Order
from ..forms import AssigneeForm
from coaster.views import load_models
from order import jsonify_assignee
from boxoffice.mailclient import send_ticket_assignment_mail
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
    if not request.json.get('assignee'):
        return make_response(jsonify(status='error', error='missing_attendee_details', error_description="Attendee details are missing"), 400)

    line_item = LineItem.query.get(request.json.get('line_item_id'))
    if line_item.is_cancelled:
        return make_response(jsonify(status='error', error='cancelled_ticket', error_description="Ticket has been cancelled"), 400)

    assignee_request_dict = request.json.get('assignee')
    assignee_form = AssigneeForm.from_json(assignee_request_dict)
    assignee_form.csrf_enabled = False
    if not assignee_form.validate():
        return make_response(jsonify(message='Invalid attendee details'), 400)

    item_assignee_details = line_item.item.assignee_details
    assignee_details = {}
    for key in item_assignee_details.keys():
        assignee_details[key] = assignee_request_dict.get(key)

    if line_item.current_assignee and assignee_form.data.get('email') == line_item.current_assignee.email:
        # updating details of the current assignee
        line_item.current_assignee.fullname = assignee_form.data.get('fullname')
        line_item.current_assignee.phone = assignee_form.data.get('phone')
        line_item.current_assignee.details = assignee_details
        db.session.commit()
    else:
        if line_item.current_assignee:
            if not line_item.is_transferrable():
                return make_response(jsonify(status='error', error='ticket_not_transferrable', error_description="Ticket cannot be transferred."), 400)
            # Archive current assignee
            previous_assignee_email = line_item.current_assignee.email
            line_item.current_assignee.current = None
        else:
            previous_assignee_email = None
        new_assignee = Assignee(current=True, email=assignee_form.data.get('email'), fullname=assignee_form.data.get('fullname'),
            phone=assignee_form.data.get('phone'), details=assignee_details, line_item=line_item)
        db.session.add(new_assignee)
        db.session.commit()
        if previous_assignee_email:
            cc_list = [line_item.order.buyer_email, previous_assignee_email]
        else:
            cc_list = [line_item.order.buyer_email]
        recipient_list = [line_item.current_assignee.email]
        send_ticket_assignment_mail.delay(line_item.id, recipient_list, cc_list)
    return make_response(jsonify(status='ok', result={'message': 'Ticket assigned', 'assignee': jsonify_assignee(line_item.current_assignee)}), 201)
