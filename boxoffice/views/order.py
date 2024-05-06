from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal, NotRequired, TypedDict, cast, overload
from uuid import UUID

from flask import Response, abort, jsonify, render_template, request, url_for
from werkzeug.datastructures import ImmutableMultiDict

from baseframe import _, localized_country_list
from baseframe.forms import render_form
from coaster.utils import utcnow
from coaster.views import ReturnRenderWith, load_models, render_with

from .. import app, lastuser
from ..data import indian_states
from ..extapi import razorpay
from ..forms import (
    BuyerForm,
    InvoiceForm,
    LineItemForm,
    OrderRefundForm,
    OrderSessionForm,
)
from ..mailclient import (
    send_line_item_cancellation_mail,
    send_order_refund_mail,
    send_receipt_mail,
)
from ..models import (
    Assignee,
    CurrencyEnum,
    CurrencySymbol,
    DiscountCoupon,
    DiscountPolicy,
    Invoice,
    LineItem,
    LineItemStatus,
    LineItemTuple,
    Menu,
    OnlinePayment,
    Order,
    OrderSession,
    OrderStatus,
    PaymentTransaction,
    RazorpayPaymentStatus,
    Ticket,
    TransactionTypeEnum,
    User,
    db,
    sa,
)
from .custom_exceptions import PaymentGatewayError
from .utils import (
    api_error,
    api_success,
    cors,
    json_date_format,
    sanitize_coupons,
    xhr_only,
)


class LineItemData(TypedDict):
    is_available: bool
    quantity: int
    base_amount: NotRequired[Decimal]
    final_amount: Decimal | None
    discounted_amount: Decimal | None
    discount_policy_ids: list[UUID]
    quantity_available: NotRequired[int]


class AssigneeDict(TypedDict):
    id: int
    fullname: str
    email: str
    phone: str | None
    details: dict


def jsonify_line_items(line_items: Iterable[LineItemTuple]) -> dict[str, LineItemData]:
    """
    Serialize and return line items.

    Format::

        {
            ticket_id: {
                'quantity': Y,
                'final_amount': Z,
                'discounted_amount': Z,
                'discount_policy_ids': ['d1', 'd2']
            }
        }
    """
    items_json: dict[str, LineItemData] = {}
    for line_item in line_items:
        ticket = Ticket.query.get_or_404(line_item.ticket_id)
        ticket_id = str(line_item.ticket_id)
        if ticket_id not in items_json:
            items_json[ticket_id] = {
                'is_available': ticket.is_available,
                'quantity': 0,
                'final_amount': Decimal(0),
                'discounted_amount': Decimal(0),
                'discount_policy_ids': [],
            }
        if line_item.base_amount is not None:
            items_json[ticket_id]['base_amount'] = line_item.base_amount
            items_json[ticket_id]['final_amount'] = (
                items_json[ticket_id]['final_amount'] or Decimal('0')
            ) + (line_item.base_amount - (line_item.discounted_amount or Decimal('0')))
            items_json[ticket_id]['discounted_amount'] = (
                items_json[ticket_id]['discounted_amount'] or Decimal('0')
            ) + (line_item.discounted_amount or Decimal('0'))
            items_json[ticket_id]['quantity_available'] = ticket.quantity_available
        else:
            items_json[ticket_id]['final_amount'] = None
            items_json[ticket_id]['discounted_amount'] = None

        items_json[ticket_id]['quantity'] += 1
        if (
            line_item.discount_policy_id
            and line_item.discount_policy_id
            not in items_json[ticket_id]['discount_policy_ids']
        ):
            items_json[ticket_id]['discount_policy_ids'].append(
                line_item.discount_policy_id
            )
    return items_json


@overload
def jsonify_assignee(assignee: None) -> None: ...


@overload
def jsonify_assignee(assignee: Assignee) -> AssigneeDict: ...


def jsonify_assignee(assignee: Assignee | None) -> AssigneeDict | None:
    if assignee is not None:
        return {
            'id': assignee.id,
            'fullname': assignee.fullname,
            'email': assignee.email,
            'phone': assignee.phone,
            'details': assignee.details,
        }
    return None


def jsonify_order(data: Mapping[str, Any]) -> Response:
    order = data['order']
    line_items = []
    for line_item in order.line_items:
        line_items.append(
            {
                'seq': line_item.line_item_seq,
                'id': line_item.id,
                'title': line_item.ticket.title,
                'description': line_item.ticket.description.text,
                'description_html': line_item.ticket.description.html,
                'final_amount': line_item.final_amount,
                'assignee_details': line_item.ticket.assignee_details,
                'assignee': jsonify_assignee(line_item.current_assignee),
                'is_confirmed': line_item.is_confirmed,
                'is_cancelled': line_item.is_cancelled,
                'cancelled_at': (
                    json_date_format(line_item.cancelled_at)
                    if line_item.cancelled_at
                    else ""
                ),
                'is_transferable': line_item.is_transferable,
            }
        )
    return jsonify(
        order_id=order.id,
        access_token=order.access_token,
        menu_name=order.menu.name,
        menu_title=order.menu.title,
        buyer_name=order.buyer_fullname,
        buyer_email=order.buyer_email,
        buyer_phone=order.buyer_phone,
        line_items=line_items,
    )


@app.route('/order/kharcha', methods=['OPTIONS', 'POST'])
@xhr_only
@cors
def kharcha() -> Response:
    """
    Calculate rates for an order of items and quantities.

    Accepts JSON containing an array of line_items, with the quantity and ticket_id set
    for each line_item.

    Returns JSON of line items in the format::

        {
            ticket_id: {
                "quantity": Y,
                "final_amount": Z,
                "discounted_amount": Z,
                "discount_policy_ids": ["d1", "d2"]
            }
        }
    """
    if not request.json or not request.json.get('line_items'):
        return api_error(message='Missing line items', status_code=400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items', []))
    if not line_item_forms:
        return api_error(message='Missing line items', status_code=400)

    # Make line item splits and compute amounts and discounts
    line_items = LineItem.calculate(
        [
            {'ticket_id': li_form.data.get('ticket_id')}
            for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))
        ],
        coupons=sanitize_coupons(request.json.get('discount_coupons')),
    )
    items_json = jsonify_line_items(line_items)
    order_final_amount = sum(
        values['final_amount']
        for values in items_json.values()
        if values['final_amount'] is not None
    )
    return jsonify(line_items=items_json, order={'final_amount': order_final_amount})


@app.route('/menu/<menu_id>/order', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((Menu, {'id': 'menu_id'}, 'menu'))
def create_order(menu: Menu) -> Response:
    """
    Create an order.

    Accepts JSON containing an array of line_items with the quantity and ticket_id
    set for each ticket, and a buyer hash containing `email`, `fullname` and `phone`.

    Creates a purchase order, and returns a JSON containing the final_amount, order id
    and the URL to be used to register a payment against the order.
    """
    if not request.json or not request.json.get('line_items'):
        return api_error(message=_("Missing line items"), status_code=400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items', []))
    if not line_item_forms:
        return api_error(message=_("Invalid line items"), status_code=400)
    # See comment in LineItemForm about CSRF
    buyer_form = BuyerForm(
        formdata=ImmutableMultiDict(request.json.get('buyer')), meta={'csrf': False}
    )
    if not buyer_form.validate():
        return api_error(
            message=_("Invalid buyer details"),
            status_code=400,
            errors=buyer_form.errors,
        )

    invalid_quantity_error_msg = _(
        "Selected quantity for ‘{ticket}’ is not available. Please edit the order and"
        " update the quantity"
    )
    ticket_dicts = Ticket.get_availability(
        [line_item_form.data.get('ticket_id') for line_item_form in line_item_forms]
    )

    for line_item_form in line_item_forms:
        title_quantity_count = ticket_dicts.get(line_item_form.data.get('ticket_id'))
        if title_quantity_count:
            ticket_title, ticket_quantity_total, line_item_count = title_quantity_count
            if (
                line_item_count + line_item_form.data.get('quantity')
            ) > ticket_quantity_total:
                return api_error(
                    message=invalid_quantity_error_msg.format(ticket=ticket_title),
                    status_code=400,
                    errors=['order calculation error'],
                )
        else:
            ticket = Ticket.query.get_or_404(line_item_form.data.get('ticket_id'))
            if line_item_form.data.get('quantity') > ticket.quantity_total:
                return api_error(
                    message=invalid_quantity_error_msg.format(ticket=ticket.title),
                    status_code=400,
                    errors=['order calculation error'],
                )

    user = User.query.filter_by(email=buyer_form.email.data).one_or_none()
    order = Order(
        user=user,
        organization=menu.organization,
        menu=menu,
        buyer_email=buyer_form.email.data,
        buyer_fullname=buyer_form.fullname.data,
        buyer_phone=buyer_form.phone.data,
    )

    sanitized_coupon_codes = sanitize_coupons(request.json.get('discount_coupons'))
    line_item_tups = LineItem.calculate(
        [
            {'ticket_id': li_form.data.get('ticket_id')}
            for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))
        ],
        coupons=sanitized_coupon_codes,
    )

    for idx, line_item_tup in enumerate(line_item_tups):
        ticket = Ticket.query.get_or_404(line_item_tup.ticket_id)

        if ticket.restricted_entry and (
            not sanitized_coupon_codes
            or not DiscountPolicy.is_valid_access_coupon(ticket, sanitized_coupon_codes)
        ):
            # Skip adding a restricted ticket to cart without the proper access code
            break

        if ticket.is_available:
            if line_item_tup.discount_policy_id:
                policy = DiscountPolicy.query.get_or_404(
                    line_item_tup.discount_policy_id
                )
            else:
                policy = None
            if line_item_tup.discount_coupon_id:
                coupon = DiscountCoupon.query.get_or_404(
                    line_item_tup.discount_coupon_id
                )
            else:
                coupon = None

            line_item = LineItem(
                order=order,
                ticket=ticket,
                discount_policy=policy,
                line_item_seq=idx + 1,
                discount_coupon=coupon,
                ordered_at=utcnow(),
                base_amount=line_item_tup.base_amount,
                discounted_amount=line_item_tup.discounted_amount,
                final_amount=cast(Decimal, line_item_tup.base_amount)
                - cast(Decimal, line_item_tup.discounted_amount),
            )
            db.session.add(line_item)
        else:
            return api_error(
                message=_("‘{ticket}’ is no longer available.").format(
                    ticket=ticket.title
                ),
                status_code=400,
                errors=['order calculation error'],
            )

    db.session.add(order)

    if request.json.get('order_session'):
        order_session_form = OrderSessionForm(
            formdata=ImmutableMultiDict(request.json.get('order_session')),
            meta={'csrf': False},
        )
        if order_session_form.validate():
            order_session = OrderSession(order=order)
            order_session_form.populate_obj(order_session)
            db.session.add(order_session)

    db.session.commit()

    return api_success(
        doc=_("New purchase order created"),
        result={
            'order_id': order.id,
            'order_access_token': order.access_token,
            'payment_url': url_for('capture_payment', order=order.id),
            'free_order_url': url_for('free', order=order.id),
            'final_amount': order.get_amounts(
                LineItemStatus.PURCHASE_ORDER
            ).final_amount,
        },
        status_code=201,
    )


@app.route('/order/<order>/free', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((Order, {'id': 'order'}, 'order'))
def free(order: Order) -> Response:
    """Complete a order which has a final_amount of 0."""
    order_amounts = order.get_amounts(LineItemStatus.PURCHASE_ORDER)
    if order_amounts.final_amount == 0:
        order.confirm_sale()
        db.session.add(order)
        db.session.commit()
        for line_item in order.line_items:
            line_item.confirm()
            db.session.add(line_item)
            if line_item.discount_coupon:
                line_item.discount_coupon.update_used_count()
                db.session.add(line_item.discount_coupon)
        db.session.commit()
        send_receipt_mail.queue(
            order.id,
            subject=_("{menu_title}: Your registration is confirmed!").format(
                menu_title=order.menu.title
            ),
            template='free_order_confirmation_mail.html.jinja2',
        )
        return api_success(
            result={'order_id': order.id},
            doc=_("Free order confirmed"),
            status_code=201,
        )

    return api_error(message=_("Free order confirmation failed"), status_code=422)


@app.route('/order/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((Order, {'id': 'order'}, 'order'))
def capture_payment(order: Order) -> Response:
    """
    Capture a payment.

    Accepts JSON containing `pg_paymentid`. Creates a payment object, attempts to
    'capture' the payment from Razorpay, and returns a JSON containing the result of the
    operation.

    A successful capture results in a `payment_transaction` registered against the
    order.
    """
    if TYPE_CHECKING:
        assert request.json is not None  # nosec B101
    if not request.json.get('pg_paymentid'):
        return api_error(message=_("Missing payment id"), status_code=400)

    order_amounts = order.get_amounts(LineItemStatus.PURCHASE_ORDER)
    online_payment = OnlinePayment(
        pg_paymentid=request.json.get('pg_paymentid'), order=order
    )

    rp_resp = razorpay.capture_payment(
        online_payment.pg_paymentid, order_amounts.final_amount
    )
    if rp_resp.status_code == 200:
        online_payment.confirm()
        db.session.add(online_payment)
        # Only INR is supported as of now
        transaction = PaymentTransaction(
            order=order,
            online_payment=online_payment,
            amount=order_amounts.final_amount,
            currency=CurrencyEnum.INR,
        )
        db.session.add(transaction)
        order.confirm_sale()
        db.session.add(order)
        invoice_organization = (
            order.organization.invoicer
            if order.organization.invoicer
            else order.organization
        )
        invoice = Invoice(order=order, organization=invoice_organization)
        db.session.add(invoice)
        db.session.commit()
        for line_item in order.line_items:
            line_item.confirm()
            db.session.add(line_item)
            if line_item.discount_coupon:
                line_item.discount_coupon.update_used_count()
                db.session.add(line_item.discount_coupon)
        db.session.commit()
        send_receipt_mail.queue(
            order.id,
            subject=_("{menu_title}: Thank you for your order (#{receipt_no})!").format(
                menu_title=order.menu.title,
                receipt_no=order.receipt_no,
            ),
        )
        return api_success(
            result={'invoice_id': invoice.id},
            doc=_("Payment verified"),
            status_code=201,
        )
    online_payment.fail()
    db.session.add(online_payment)
    db.session.commit()
    raise PaymentGatewayError(
        _("Online payment failed for order #{order}: {msg}").format(
            order=order.id, msg=rp_resp.content
        ),
        424,
        _("Your payment failed. Try again, or contact us at {email}.").format(
            email=order.organization.contact_email
        ),
    )


@app.route('/order/<access_token>/receipt', methods=['GET'])
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def receipt(order: Order) -> str:
    if not order.is_confirmed:
        abort(404)
    line_items = LineItem.query.filter(
        LineItem.order == order, LineItem.status == LineItemStatus.CONFIRMED
    ).all()
    return render_template(
        'cash_receipt.html.jinja2',
        order=order,
        org=order.organization,
        line_items=line_items,
        currency_symbol=CurrencySymbol.INR,
    )


class InvoiceDict(TypedDict):
    id: UUID
    buyer_taxid: str | None
    invoicee_name: str | None
    invoicee_company: str | None
    invoicee_email: str | None
    street_address_1: str | None
    street_address_2: str | None
    city: str | None
    postcode: str | None
    country_code: str | None
    state_code: str | None
    state: str | None


def jsonify_invoice(invoice: Invoice) -> InvoiceDict:
    return {
        'id': invoice.id,
        'buyer_taxid': invoice.buyer_taxid,
        'invoicee_name': invoice.invoicee_name,
        'invoicee_company': invoice.invoicee_company,
        'invoicee_email': invoice.invoicee_email,
        'street_address_1': invoice.street_address_1,
        'street_address_2': invoice.street_address_2,
        'city': invoice.city,
        'postcode': invoice.postcode,
        'country_code': invoice.country_code,
        'state_code': invoice.state_code,
        'state': invoice.state,
    }


@app.route('/order/<access_token>/invoice', methods=['OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def edit_invoice_details(order: Order) -> Response:
    """Update invoice with buyer's address and tax id."""
    if TYPE_CHECKING:
        assert request.json is not None  # nosec B101
    if not order.is_confirmed:
        abort(404)
    invoice_dict = request.json.get('invoice', {})
    if not request.json or not invoice_dict:
        return api_error(message=_("Missing invoice details"), status_code=400)

    invoice = Invoice.query.get_or_404(request.json.get('invoice_id'))
    if invoice.is_final:
        return api_error(
            message=_("This invoice has been finalised and hence cannot be modified"),
            status_code=400,
        )

    invoice_form = InvoiceForm(
        formdata=ImmutableMultiDict(invoice_dict), meta={'csrf': False}
    )
    if not invoice_form.validate():
        return api_error(
            message=_("Incorrect invoice details"),
            status_code=400,
            errors=invoice_form.errors,
        )
    invoice_form.populate_obj(invoice)
    db.session.commit()
    return api_success(
        result={'message': 'Invoice updated', 'invoice': jsonify_invoice(invoice)},
        doc=_("Invoice details added"),
        status_code=201,
    )


def jsonify_invoices(data_dict: Mapping[str, Any]) -> Response:
    invoices_list = []
    for invoice in data_dict['invoices']:
        invoices_list.append(jsonify_invoice(invoice))
    return jsonify(
        invoices=invoices_list,
        access_token=data_dict['order'].access_token,
        states=[{'name': state.title, 'code': state.name} for state in indian_states],
        countries=[
            {'name': name, 'code': code} for code, name in localized_country_list()
        ],
    )


@app.route('/order/<access_token>/invoice', methods=['GET'])
@render_with(
    {'text/html': 'invoice_form.html.jinja2', 'application/json': jsonify_invoices}
)
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def invoice_details_form(order: Order) -> ReturnRenderWith:
    """View all invoices of an order."""
    if not order.is_confirmed:
        abort(404)
    if not order.invoices:
        invoice = Invoice(order=order, organization=order.organization)
        db.session.add(invoice)
        db.session.commit()
    invoices = order.invoices

    return {'order': order, 'org': order.organization, 'invoices': invoices}


@app.route('/order/<access_token>/ticket', methods=['GET', 'POST'])
@render_with(
    {'text/html': 'order.html.jinja2', 'application/json': jsonify_order}, json=True
)
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def order_ticket(order: Order) -> ReturnRenderWith:
    return {'order': order, 'org': order.organization}


class TicketDict(TypedDict):
    title: str


class LineItemDict(TypedDict):
    assignee: dict[str, Any]
    line_item_seq: int
    line_item_status: Literal['confirmed', 'cancelled']
    ticket: TicketDict


class OrdersDict(TypedDict):
    receipt_no: int | None
    line_items: list[LineItemDict]


def format_assignee(line_item: LineItem) -> dict[str, Any]:
    if not line_item.current_assignee:
        return {}
    assignee = {
        'fullname': line_item.current_assignee.fullname,
        'email': line_item.current_assignee.email,
        'phone': line_item.current_assignee.phone,
    }

    for key in line_item.ticket.assignee_details:
        assignee[key] = line_item.current_assignee.details.get(key)
    return assignee


def jsonify_orders(orders: Iterable[Order]) -> list[OrdersDict]:
    api_orders = []

    for order in orders:
        order_dict: OrdersDict = {'receipt_no': order.receipt_no, 'line_items': []}
        for line_item in order.line_items:
            order_dict['line_items'].append(
                {
                    'assignee': format_assignee(line_item),
                    'line_item_seq': line_item.line_item_seq,
                    'line_item_status': (
                        "confirmed" if line_item.is_confirmed else "cancelled"
                    ),
                    'ticket': {'title': line_item.ticket.title},
                }
            )
        api_orders.append(order_dict)
    return api_orders


def get_coupon_codes_from_line_items(line_items: Iterable[LineItem]) -> list[str]:
    coupon_ids = [
        line_item.discount_coupon.id
        for line_item in line_items
        if line_item.discount_coupon
    ]
    if coupon_ids:
        coupons = (
            DiscountCoupon.query.filter(DiscountCoupon.id.in_(coupon_ids))
            .options(sa.orm.load_only(DiscountCoupon.code))
            .all()
        )
    else:
        coupons = []
    return [coupon.code for coupon in coupons]


def regenerate_line_item(
    order: Order,
    original_line_item: LineItem,
    updated_line_item_tup: LineItemTuple,
    line_item_seq: int,
) -> LineItem:
    """Update a line item by marking the original as void and creating a replacement."""
    assert updated_line_item_tup.base_amount is not None  # noqa: S101  # nosec B101
    assert (  # noqa: S101  # nosec B101
        updated_line_item_tup.discounted_amount is not None
    )
    original_line_item.make_void()
    ticket = Ticket.query.get_or_404(updated_line_item_tup.ticket_id)
    if updated_line_item_tup.discount_policy_id:
        policy = DiscountPolicy.query.get_or_404(
            updated_line_item_tup.discount_policy_id
        )
    else:
        policy = None
    if updated_line_item_tup.discount_coupon_id:
        coupon = DiscountCoupon.query.get_or_404(
            updated_line_item_tup.discount_coupon_id
        )
    else:
        coupon = None

    return LineItem(
        order=order,
        ticket=ticket,
        discount_policy=policy,
        previous=original_line_item,
        status=LineItemStatus.CONFIRMED,
        line_item_seq=line_item_seq,
        discount_coupon=coupon,
        ordered_at=utcnow(),
        base_amount=updated_line_item_tup.base_amount,
        discounted_amount=updated_line_item_tup.discounted_amount,
        final_amount=updated_line_item_tup.base_amount
        - updated_line_item_tup.discounted_amount,
    )


def update_order_on_line_item_cancellation(
    order: Order,
    pre_cancellation_line_items: Iterable[LineItem],
    cancelled_line_item: LineItem,
) -> Order:
    """Cancel the given line item and update the order."""
    active_line_items = [
        pre_cancellation_line_item
        for pre_cancellation_line_item in pre_cancellation_line_items
        if pre_cancellation_line_item != cancelled_line_item
    ]
    recalculated_line_item_tups = LineItem.calculate(
        active_line_items,
        coupons=get_coupon_codes_from_line_items(active_line_items),
    )

    last_line_item_seq = LineItem.get_max_seq(order)
    for idx, line_item_tup in enumerate(
        recalculated_line_item_tups, start=last_line_item_seq + 1
    ):
        # Fetch the line item object
        pre_cancellation_line_item = next(
            pre_cancellation_line_item
            for pre_cancellation_line_item in pre_cancellation_line_items
            if pre_cancellation_line_item.id == line_item_tup.id
        )
        # Check if the line item's amount has changed post-cancellation
        if line_item_tup.final_amount != pre_cancellation_line_item.final_amount:
            # Amount has changed, void this line item and regenerate the line item
            updated_line_item = regenerate_line_item(
                order, pre_cancellation_line_item, line_item_tup, idx
            )
            db.session.add(updated_line_item)
            current_assignee = pre_cancellation_line_item.current_assignee
            if current_assignee:
                db.session.add(
                    Assignee(
                        current=True,
                        email=current_assignee.email,
                        fullname=current_assignee.fullname,
                        phone=current_assignee.phone,
                        details=current_assignee.details,
                        line_item=updated_line_item,
                    )
                )
    return order


def process_line_item_cancellation(line_item: LineItem) -> Decimal:
    order = line_item.order
    # initialize refund_amount to 0
    refund_amount = Decimal(0)

    if (not line_item.is_free) and order.net_amount > Decimal('0'):
        if line_item.discount_policy:
            pre_cancellation_order_amount = (
                order.get_amounts(LineItemStatus.CONFIRMED).confirmed_amount
                - order.refunded_amount
            )
            pre_cancellation_line_items = order.confirmed_line_items
            line_item.cancel()
            updated_order = update_order_on_line_item_cancellation(
                order, pre_cancellation_line_items, line_item
            )
            post_cancellation_order_amount = (
                updated_order.get_amounts(LineItemStatus.CONFIRMED).confirmed_amount
                - order.refunded_amount
            )
            refund_amount = (
                pre_cancellation_order_amount - post_cancellation_order_amount
            )
        else:
            line_item.cancel()
            refund_amount = line_item.final_amount

        # If the refund amount exceeds the net amount received (after prior refunds),
        # reduce the refund to the remaining net amount
        refund_amount = min(refund_amount, order.net_amount)

    if refund_amount > Decimal('0'):
        payment = OnlinePayment.query.filter_by(
            order=line_item.order, pg_payment_status=RazorpayPaymentStatus.CAPTURED
        ).one()
        rp_resp = razorpay.refund_payment(payment.pg_paymentid, refund_amount)
        rp_refund = rp_resp.json()
        if rp_resp.status_code == 200:
            db.session.add(
                PaymentTransaction(
                    order=order,
                    transaction_type=TransactionTypeEnum.REFUND,
                    pg_refundid=rp_refund['id'],
                    online_payment=payment,
                    amount=refund_amount,
                    currency=CurrencyEnum.INR,
                    refunded_at=sa.func.utcnow(),
                    refund_description=_("Refund: {line_item_title}").format(
                        line_item_title=line_item.ticket.title
                    ),
                )
            )
        else:
            raise PaymentGatewayError(
                _("Cancellation failed for order #{order}: {msg}").format(
                    order=order.id, msg=rp_refund['error']['description']
                ),
                424,
                _(
                    "Refund failed with “{reason}”. Try again, or write to us at"
                    " {email}."
                ).format(
                    reason=rp_refund['error']['description'],
                    email=line_item.order.organization.contact_email,
                ),
            )
    else:
        # no refund applicable, just cancel the line item
        line_item.cancel()
    db.session.commit()
    return refund_amount


@app.route('/line_item/<line_item_id>/cancel', methods=['POST'])
@lastuser.requires_login
@load_models((LineItem, {'id': 'line_item_id'}, 'line_item'), permission='org_admin')
def cancel_line_item(line_item: LineItem) -> Response:
    if not line_item.is_cancellable():
        return api_error(
            message='This ticket is not cancellable',
            status_code=403,
            errors=['non cancellable'],
        )

    refund_amount = process_line_item_cancellation(line_item)
    send_line_item_cancellation_mail.queue(line_item.id, refund_amount)
    return api_success(
        result={'cancelled_at': json_date_format(line_item.cancelled_at)},
        doc=_("Ticket cancelled"),
        status_code=200,
    )


def process_partial_refund_for_order(data_dict: Mapping[str, Any]) -> Response:
    order = data_dict['order']
    form = data_dict['form']
    request_method = data_dict['request_method']

    if request_method == 'GET':
        return jsonify(
            form_template=render_form(
                form=form,
                title=_("Partial refund"),
                submit=_("Refund"),
                with_chrome=False,
            ).get_data(as_text=True)
        )
    if form.validate_on_submit():
        requested_refund_amount = form.amount.data
        payment = OnlinePayment.query.filter_by(
            order=order, pg_payment_status=RazorpayPaymentStatus.CAPTURED
        ).one()
        rp_resp = razorpay.refund_payment(payment.pg_paymentid, requested_refund_amount)
        rp_refund = rp_resp.json()
        if rp_resp.status_code == 200:
            transaction = PaymentTransaction(
                order=order,
                transaction_type=TransactionTypeEnum.REFUND,
                online_payment=payment,
                currency=CurrencyEnum.INR,
                pg_refundid=rp_refund['id'],
                refunded_at=sa.func.utcnow(),
            )
            form.populate_obj(transaction)
            db.session.add(transaction)
            db.session.commit()
            send_order_refund_mail.queue(
                order.id, transaction.amount, transaction.note_to_user
            )
            return api_success(
                result={'order_net_amount': order.net_amount},
                doc=_("Refund processed for order"),
                status_code=200,
            )
        raise PaymentGatewayError(
            _("Refund failed for order #{order}: {msg}").format(
                order=order.id, msg=rp_refund['error']['description']
            ),
            424,
            _(
                "Refund failed with “{reason}”. Try again, or contact support at"
                " {email}."
            ).format(
                reason=rp_refund['error']['description'],
                email=order.organization.contact_email,
            ),
        )
    return api_error(message='Invalid input', status_code=403, errors=form.errors)


@app.route(
    '/admin/menu/<menu_id>/order/<order_id>/partial_refund', methods=['GET', 'POST']
)
@lastuser.requires_login
@render_with(
    {
        'text/html': 'index.html.jinja2',
        'application/json': process_partial_refund_for_order,
    }
)
@load_models((Order, {'id': 'order_id'}, 'order'), permission='org_admin')
def partial_refund_order(order: Order) -> ReturnRenderWith:
    return {
        'order': order,
        'form': OrderRefundForm(parent=order),
        'request_method': request.method,
    }


@app.route('/api/1/ic/<menu_id>/orders', methods=['GET', 'OPTIONS'])
@app.route('/api/1/menu/<menu_id>/orders', methods=['GET', 'OPTIONS'])
@load_models((Menu, {'id': 'menu_id'}, 'menu'))
def menu_orders(menu: Menu) -> Response:
    organization = menu.organization
    # TODO: Replace with a better authentication system
    if not request.args.get('access_token') or request.args.get(
        'access_token'
    ) != organization.details.get("access_token"):
        abort(401)
    orders = menu.orders.filter(
        Order.status.in_([OrderStatus.SALES_ORDER.value, OrderStatus.INVOICE.value])
    ).all()
    return jsonify(orders=jsonify_orders(orders))
