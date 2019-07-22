# -*- coding: utf-8 -*-

from flask import jsonify, make_response, request

from boxoffice.mailclient import send_ticket_assignment_mail
from utils import xhr_only

from coaster.views import load_models, render_with

from .. import app
from ..forms import AssigneeForm
from ..models import Assignee, LineItem, Order, db


@app.route('/participant/<access_token>/assign', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@render_with(json=True)
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def assign(order):
    """
    Assign a line_item to a participant
    """
    line_item = LineItem.query.get(request.json.get('line_item_id'))
    if line_item is None:
        return {
            'status': 'error',
            'error': 'missing_line_item',
            'error_description': u"Invalid line item",
        }, 404
    elif line_item.is_cancelled:
        return (
            {
                'status': 'error',
                'error': 'cancelled_ticket',
                'error_description': u"Ticket has been cancelled",
            },
            400,
        )

    assignee_form = AssigneeForm.from_json(
        request.json.get('attendee'),
        obj=line_item.current_assignee,
        parent=line_item,
        csrf_token=request.json.get('csrf_token'),
    )

    if assignee_form.validate_on_submit():
        item_assignee_details = line_item.item.assignee_details
        assignee_details = {}
        if item_assignee_details:
            for key in item_assignee_details.keys():
                assignee_details[key] = assignee_form.data.get(key)
        if (
            line_item.current_assignee
            and assignee_form.data['email'] == line_item.current_assignee.email
        ):
            # updating details of the current assignee
            line_item.current_assignee.fullname = assignee_form.data['fullname']
            line_item.current_assignee.phone = assignee_form.data['phone']
            line_item.current_assignee.details = assignee_details
            db.session.commit()
        else:
            if line_item.current_assignee:
                # Archive current assignee
                line_item.current_assignee.current = None
            new_assignee = Assignee(
                current=True,
                email=assignee_form.data.get('email'),
                fullname=assignee_form.data.get('fullname'),
                phone=assignee_form.data.get('phone'),
                details=assignee_details,
                line_item=line_item,
            )
            db.session.add(new_assignee)
            db.session.commit()
            send_ticket_assignment_mail.queue(line_item.id)
        return {'status': 'ok', 'result': {'message': 'Ticket assigned'}}
    else:
        return (
            {
                'status': 'error',
                'error': 'invalid_assignee_details',
                'error_description': ", ".join(
                    [str(err) for err_list in assignee_form.errors.values() for err in err_list]
                ),
            },
            400,
        )
