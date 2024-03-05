from datetime import timedelta
import json

from coaster.utils import utcnow

from boxoffice import app
from boxoffice.models import Item, Menu, Order, OrderStatus


def ajax_post(client, url, data):
    return client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        headers=[
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Origin', app.config['BASE_URL']),
        ],
    )


def test_assign(db_session, client, all_data) -> None:
    ticket = Item.query.filter_by(name="conference-ticket").one()
    data = {
        'line_items': [{'ticket_id': str(ticket.id), 'quantity': 2}],
        'buyer': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test@hasgeek.com',
        },
    }
    menu = Menu.query.one()
    resp = ajax_post(client, f'/menu/{menu.id}/order', data)

    assert resp.status_code == 201
    resp_data = json.loads(resp.data)['result']
    order = Order.query.get(resp_data.get('order_id'))
    assert isinstance(order, Order)
    assert order.status == OrderStatus.PURCHASE_ORDER

    assert len(order.line_items) == 2
    li_one = order.line_items[0]
    li_two = order.line_items[1]

    # li_one has no assingee set yet, so it should be possible to set one
    assert li_one.assignee is None
    assert li_one.current_assignee is None
    data = {
        'line_item_id': str(li_one.id),
        'attendee': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test11@hasgeek.com',
        },
    }
    resp = ajax_post(
        client,
        f'/participant/{order.access_token}/assign',
        data,
    )
    assert json.loads(resp.data)['status'] == 'ok'
    assert li_one.assignee is not None
    assert li_one.current_assignee is not None  # type: ignore[unreachable]

    # Now assigning the other line item to same email address should fail
    data = {
        'line_item_id': str(li_two.id),
        'attendee': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test11@hasgeek.com',
        },
    }
    resp = ajax_post(
        client,
        f'/participant/{order.access_token}/assign',
        data,
    )
    assert json.loads(resp.data)['status'] == 'error'

    # But reassigning li_one should still work
    data = {
        'line_item_id': str(li_one.id),
        'attendee': {
            'fullname': 'Testing',
            'phone': '9814141414',
            'email': 'test12@hasgeek.com',  # email is the measure of uniqueness
        },
    }
    resp = ajax_post(
        client,
        f'/participant/{order.access_token}/assign',
        data,
    )
    assert json.loads(resp.data)['status'] == 'ok'

    # if no transferable_until is set, and no event_date is set,
    # transfer is allowed indefinitely.
    ticket.transferable_until = None
    ticket.event_date = None
    db_session.commit()

    assert li_one.is_transferable is True

    ticket.transferable_until = utcnow() + timedelta(days=2)
    ticket.event_date = utcnow() + timedelta(days=2)
    db_session.commit()

    # let's set transferable_until date to a past date,
    # so now another transfer of li_one should fail
    ticket.transferable_until = utcnow() - timedelta(days=2)
    db_session.commit()

    data = {
        'line_item_id': str(li_one.id),
        'attendee': {
            'fullname': 'Testing',
            'phone': '9814141415',
            'email': 'test13@hasgeek.com',
        },
    }
    resp = ajax_post(
        client,
        f'/participant/{order.access_token}/assign',
        data,
    )
    assert json.loads(resp.data)['status'] == 'error'

    # li_two still doesn't have an assignee
    assert li_two.assignee is None
    assert li_two.current_assignee is None

    # if `ticket.event_date` is in the past, and
    # `transferable_until` is not set,
    # ticket assign should still be allowed.
    # ticket assign doesn't have a deadline right now.
    ticket.event_date = utcnow().date() - timedelta(days=2)
    ticket.transferable_until = None
    db_session.commit()

    data = {
        'line_item_id': str(li_two.id),
        'attendee': {
            'fullname': 'Testing',
            'phone': '9814141415',
            'email': 'test21@hasgeek.com',
        },
    }
    resp = ajax_post(
        client,
        f'/participant/{order.access_token}/assign',
        data,
    )
    assert json.loads(resp.data)['status'] == 'ok'

    # but ticket transfer has a hard deadline in the
    # absense of  'transferable_until' - `event_date`.
    # so, if `transferable_until` is not set and `event_date` is in the past,
    # ticket transfer should fail.
    assert li_two.assignee is not None
    assert li_two.current_assignee is not None

    ticket.event_date = utcnow().date() - timedelta(days=2)
    ticket.transferable_until = None
    db_session.commit()

    data = {
        'line_item_id': str(li_two.id),
        'attendee': {
            'fullname': 'Testing',
            'phone': '9814141415',
            'email': 'test22@hasgeek.com',
        },
    }
    resp = ajax_post(
        client,
        f'/participant/{order.access_token}/assign',
        data,
    )
    assert json.loads(resp.data)['status'] == 'error'
