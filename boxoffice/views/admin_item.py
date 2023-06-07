from typing import Optional

from flask import jsonify, request

from baseframe import _
from baseframe.forms import render_form
from coaster.utils import utcnow
from coaster.views import load_models, render_with, requestargs

from .. import app, lastuser
from ..forms import ItemForm, PriceForm
from ..models import Item, ItemCollection, Organization, Price, db, sa
from .utils import api_error, api_success, json_date_format, xhr_only


@app.route('/admin/o/<org>/items')
@lastuser.requires_login
@xhr_only
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
@requestargs('search')
def tickets(organization: Organization, search: Optional[str] = None):
    if search:
        filtered_tickets = (
            db.session.query(Item, ItemCollection)
            .filter(
                ItemCollection.organization_id == organization.id,
                sa.or_(
                    sa.func.lower(Item.title).contains(search.lower(), autoescape=True),
                    sa.func.lower(ItemCollection.title).contains(
                        search.lower(), autoescape=True
                    ),
                ),
            )
            .join(Item.menu)
            .options(
                sa.orm.Load(Item).load_only(Item.id, Item.title),
                sa.orm.Load(ItemCollection).load_only(
                    ItemCollection.id, ItemCollection.title
                ),
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
            doc="Filtered tickets",
            status_code=200,
        )
    return api_error(message=_("Missing search query"), status_code=400)


def jsonify_price(price):
    price_details = dict(price.current_access())
    price_details['tense'] = price.tense()
    return price_details


def format_demand_curve(ticket: Item):
    result = {}
    demand_counter = 0

    for amount, quantity_demanded in reversed(ticket.demand_curve()):
        demand_counter += quantity_demanded
        result[str(amount)] = {
            'quantity_demanded': quantity_demanded,
            'demand': demand_counter,
        }
    return result


def format_ticket_details(ticket: Item):
    ticket_details = dict(ticket.current_access())
    ticket_details['sold_count'] = ticket.sold_count()
    ticket_details['free_count'] = ticket.free_count()
    ticket_details['cancelled_count'] = ticket.cancelled_count()
    ticket_details['net_sales'] = ticket.net_sales()
    ticket_details['quantity_available'] = ticket.quantity_available
    ticket_details['active_price'] = ticket.active_price
    return ticket_details


def jsonify_item(data_dict):
    ticket = data_dict['ticket']
    discount_policies_list = []
    for policy in ticket.discount_policies:
        details = dict(policy.current_access())
        if policy.is_price_based:
            dp_price = Price.query.filter(Price.discount_policy == policy).one()
            details['price_details'] = {'amount': dp_price.amount}
        discount_policies_list.append(details)

    return jsonify(
        account_name=data_dict['ticket'].menu.organization.name,
        demand_curve=format_demand_curve(ticket),
        account_title=data_dict['ticket'].menu.organization.title,
        menu_id=data_dict['ticket'].menu.id,
        menu_name=data_dict['ticket'].menu.name,
        menu_title=data_dict['ticket'].menu.title,
        ticket=format_ticket_details(data_dict['ticket']),
        prices=[
            jsonify_price(price) for price in data_dict['ticket'].standard_prices()
        ],
        discount_policies=discount_policies_list,
    )


@app.route('/admin/ticket/<ticket_id>', methods=['GET'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_item})
@load_models((Item, {'id': 'ticket_id'}, 'ticket'), permission='org_admin')
def admin_item(ticket: Item):
    return {'ticket': ticket}


def jsonify_new_ticket(data_dict):
    menu = data_dict['menu']
    ticket_form = ItemForm(parent=menu)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=ticket_form, title="New ticket", submit="Create", with_chrome=False
            ).get_data(as_text=True)
        )
    if ticket_form.validate_on_submit():
        ticket = Item(menu=menu)
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


@app.route('/admin/menu/<menu_id>/ticket/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_ticket})
@load_models((ItemCollection, {'id': 'menu_id'}, 'menu'), permission='org_admin')
def admin_new_item(menu: ItemCollection):
    return {'menu': menu}


def jsonify_edit_ticket(data_dict):
    ticket = data_dict['ticket']
    ticket_form = ItemForm(obj=ticket)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=ticket_form,
                title="Update ticket",
                submit="Update",
                with_chrome=False,
            ).get_data(as_text=True)
        )
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


@app.route('/admin/ticket/<ticket_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_ticket}
)
@load_models((Item, {'id': 'ticket_id'}, 'ticket'), permission='org_admin')
def admin_edit_item(ticket: Item):
    return {'ticket': ticket}


def jsonify_new_price(data_dict):
    ticket = data_dict['ticket']
    price_form = PriceForm(parent=ticket)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=price_form, title="New price", submit="Save", with_chrome=False
            ).get_data(as_text=True)
        )
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


@app.route('/admin/ticket/<ticket_id>/price/new', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_new_price})
@load_models((Item, {'id': 'ticket_id'}, 'ticket'), permission='org_admin')
def admin_new_price(ticket: Item):
    return {'ticket': ticket}


def jsonify_edit_price(data_dict):
    price = data_dict['price']
    price_form = PriceForm(obj=price)
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=price_form, title="Update price", submit="Save", with_chrome=False
            ).get_data(as_text=True)
        )
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


@app.route('/admin/ticket/<ticket_id>/price/<price_id>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with({'text/html': 'index.html.jinja2', 'application/json': jsonify_edit_price})
@load_models((Price, {'id': 'price_id'}, 'price'), permission='org_admin')
def admin_edit_price(price: Price):
    return {'price': price}
