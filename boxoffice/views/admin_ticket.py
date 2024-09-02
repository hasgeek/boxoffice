from typing import Any, TypedDict

from flask import Response, render_template, request
from flask.typing import ResponseReturnValue

from baseframe import _
from baseframe.forms import render_form
from coaster.utils import utcnow
from coaster.views import load_models, requestargs

from .. import app, lastuser
from ..forms import PriceForm, TicketForm
from ..models import Menu, Organization, Price, Ticket, db, sa
from .utils import (
    api_error,
    api_success,
    json_date_format,
    request_wants_json,
    xhr_only,
)


@app.route('/admin/o/<org>/tickets')
@lastuser.requires_login
@xhr_only
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
@requestargs('search')
def tickets(organization: Organization, search: str | None = None) -> Response:
    if search:
        filtered_tickets = (
            # FIXME: Query one, join the other
            db.session.query(Ticket, Menu)
            .filter(
                Menu.organization_id == organization.id,
                sa.or_(
                    sa.func.lower(Ticket.title).contains(
                        search.lower(), autoescape=True
                    ),
                    sa.func.lower(Menu.title).contains(search.lower(), autoescape=True),
                ),
            )
            .join(Ticket.menu)
            .options(
                sa.orm.Load(Ticket).load_only(Ticket.id, Ticket.title),
                sa.orm.Load(Menu).load_only(Menu.id, Menu.title),
            )
            .all()
        )
        return api_success(
            result={
                'tickets': [
                    {
                        'id': str(ticket_tuple[0].id),
                        'title': f'{ticket_tuple[1].title}: {ticket_tuple[0].title}',
                    }
                    for ticket_tuple in filtered_tickets
                ]
            },
            doc=_("Filtered tickets"),
            status_code=200,
        )
    return api_error(message=_("Missing search query"), status_code=400)


# TODO: Use TypedDict
def jsonify_price(price: Price) -> dict[str, Any]:
    price_details = dict(price.current_access())
    price_details['tense'] = price.tense()
    return price_details


class DemandData(TypedDict):
    quantity_demanded: int
    demand: int


def format_demand_curve(ticket: Ticket) -> dict[str, DemandData]:
    result: dict[str, DemandData] = {}
    demand_counter = 0

    for amount, quantity_demanded in reversed(ticket.demand_curve()):
        demand_counter += quantity_demanded
        result[str(amount)] = {
            'quantity_demanded': quantity_demanded,
            'demand': demand_counter,
        }
    return result


def format_ticket_details(ticket: Ticket) -> dict[str, Any]:
    ticket_details = dict(ticket.current_access())
    ticket_details['sold_count'] = ticket.sold_count()
    ticket_details['free_count'] = ticket.free_count()
    ticket_details['cancelled_count'] = ticket.cancelled_count()
    ticket_details['net_sales'] = ticket.net_sales()
    ticket_details['quantity_available'] = ticket.quantity_available
    ticket_details['active_price'] = ticket.active_price
    return ticket_details


@app.route('/admin/ticket/<ticket_id>', methods=['GET'])
@lastuser.requires_login
@load_models((Ticket, {'uuid_hex': 'ticket_id'}, 'ticket'), permission='org_admin')
def admin_item(ticket: Ticket) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    discount_policies_list = []
    for policy in ticket.discount_policies:
        details = dict(policy.current_access())
        if policy.is_price_based:
            dp_price = Price.query.filter(Price.discount_policy == policy).one()
            details['price_details'] = {'amount': dp_price.amount}
        discount_policies_list.append(details)

    return {
        'account_name': ticket.menu.organization.name,
        'demand_curve': format_demand_curve(ticket),
        'account_title': ticket.menu.organization.title,
        'menu_id': ticket.menu.id,
        'menu_name': ticket.menu.name,
        'menu_title': ticket.menu.title,
        'ticket': format_ticket_details(ticket),
        'prices': [jsonify_price(price) for price in ticket.standard_prices()],
        'discount_policies': discount_policies_list,
    }


@app.route('/admin/menu/<menu_id>/ticket/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Menu, {'uuid_hex': 'menu_id'}, 'menu'), permission='org_admin')
def admin_new_item(menu: Menu) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    ticket_form = TicketForm(parent=menu)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=ticket_form,
                title=_("New ticket"),
                submit=_("Create"),
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if ticket_form.validate_on_submit():
        ticket = Ticket(menu=menu)
        ticket_form.populate_obj(ticket)
        if not ticket.name:
            ticket.make_name()
        db.session.add(ticket)
        db.session.commit()
        return api_success(
            result={'ticket': dict(ticket.current_access())},
            doc=_("New ticket created"),
            status_code=201,
        )
    return api_error(
        message=_("There was a problem with creating the ticket"),
        errors=ticket_form.errors,
        status_code=400,
    )


@app.route('/admin/ticket/<ticket_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Ticket, {'uuid_hex': 'ticket_id'}, 'ticket'), permission='org_admin')
def admin_edit_item(ticket: Ticket) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    ticket_form = TicketForm(obj=ticket)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=ticket_form,
                title=_("Update ticket"),
                submit=_("Update"),
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if ticket_form.validate_on_submit():
        ticket_form.populate_obj(ticket)
        db.session.commit()
        return api_success(
            result={'ticket': dict(ticket.current_access())},
            doc=_("Item updated"),
            status_code=200,
        )
    return api_error(
        message=_("There was a problem with updating the ticket"),
        status_code=400,
        errors=ticket_form.errors,
    )


@app.route('/admin/ticket/<ticket_id>/price/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Ticket, {'uuid_hex': 'ticket_id'}, 'ticket'), permission='org_admin')
def admin_new_price(ticket: Ticket) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    price_form = PriceForm(parent=ticket)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=price_form,
                title=_("New price"),
                submit=_("Save"),
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if price_form.validate_on_submit():
        price = Price(ticket=ticket)
        price_form.populate_obj(price)
        price.title = f'{ticket.name}-price-{json_date_format(utcnow())}'
        if not price.name:
            price.make_name()
        db.session.add(price)
        db.session.commit()
        return api_success(
            result={'price': dict(price.current_access())},
            doc=_("New price created"),
            status_code=201,
        )
    return api_error(
        message=_("There was a problem with creating the price"),
        status_code=400,
        errors=price_form.errors,
    )


@app.route('/admin/ticket/<ticket_id>/price/<price_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models((Price, {'uuid_hex': 'price_id'}, 'price'), permission='org_admin')
def admin_edit_price(price: Price) -> ResponseReturnValue:
    if not request_wants_json():
        return render_template('index.html.jinja2')
    price_form = PriceForm(obj=price)
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=price_form,
                title=_("Update price"),
                submit=_("Save"),
                with_chrome=False,
            ).get_data(as_text=True)
        }
    if price_form.validate_on_submit():
        price_form.populate_obj(price)
        db.session.commit()
        return api_success(
            result={'price': dict(price.current_access())},
            doc=_("Update price {title}.").format(title=price.title),
            status_code=200,
        )
    return api_error(
        message=_("There was a problem with editing the price"),
        status_code=400,
        errors=price_form.errors,
    )
