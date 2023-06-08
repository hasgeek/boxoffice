from typing import TYPE_CHECKING

from flask import request
from werkzeug.datastructures import ImmutableMultiDict

from baseframe import _
from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app
from ..forms import AssigneeForm
from ..mailclient import send_ticket_assignment_mail, send_ticket_reassignment_mail
from ..models import Assignee, LineItem, Order, db
from .utils import xhr_only


@app.route('/participant/<access_token>/assign', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@render_with(json=True)
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def assign(order: Order) -> ReturnRenderWith:
    """Assign a line_item to a participant."""
    if TYPE_CHECKING:
        assert request.json is not None  # nosec B101
    line_item = LineItem.query.get(request.json.get('line_item_id'))
    if line_item is None:
        return (
            {
                'status': 'error',
                'error': 'missing_line_item',
                'error_description': "Invalid line item",
            },
            404,
        )
    if line_item.is_cancelled:
        return (
            {
                'status': 'error',
                'error': 'cancelled_ticket',
                'error_description': "Ticket has been cancelled",
            },
            400,
        )

    assignee_dict = request.json.get('attendee')
    assignee_form = AssigneeForm(
        formdata=ImmutableMultiDict(assignee_dict),
        obj=line_item.current_assignee,
        parent=line_item,
        csrf_token=request.json.get('csrf_token'),
    )

    if not line_item.is_transferable:
        return (
            {
                'status': 'error',
                'error': 'ticket_not_transferable',
                'error_description': _(
                    "Ticket transfer deadline is over. It can no longer be transfered."
                ),
            },
            400,
        )

    if assignee_form.validate_on_submit():
        ticket_assignee_details = line_item.ticket.assignee_details
        assignee_details = {}
        if ticket_assignee_details:
            for key in ticket_assignee_details.keys():
                assignee_details[key] = assignee_dict.get(key)
        if (
            line_item.current_assignee
            and assignee_dict['email'] == line_item.current_assignee.email
        ):
            # updating details of the current assignee
            line_item.current_assignee.fullname = assignee_dict['fullname']
            line_item.current_assignee.phone = assignee_dict['phone']
            line_item.current_assignee.details = assignee_details
            db.session.commit()
        else:
            old_assignee = None
            if line_item.current_assignee:
                # Assignee is being changed. Archive current assignee.
                old_assignee = line_item.current_assignee
                line_item.current_assignee.current = None

            new_assignee = Assignee(
                current=True,
                email=assignee_dict.get('email'),
                fullname=assignee_dict.get('fullname'),
                phone=assignee_dict.get('phone'),
                details=assignee_details,
                line_item=line_item,
            )

            db.session.add(new_assignee)
            db.session.commit()
            send_ticket_assignment_mail.queue(line_item.id)

            if old_assignee is not None:
                # Send notification to previous assignee
                send_ticket_reassignment_mail.queue(
                    line_item.id, old_assignee.id, new_assignee.id
                )
        return {'status': 'ok', 'result': {'message': _("Ticket assigned")}}
    return (
        {
            'status': 'error',
            'error': 'invalid_assignee_details',
            'error_description': "Invalid form values. Please resubmit.",
            'error_details': assignee_form.errors,
        },
        400,
    )
