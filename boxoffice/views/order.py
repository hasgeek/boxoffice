from decimal import Decimal

from sqlalchemy.sql import func

from flask import abort, jsonify, render_template, request, url_for

from baseframe import _, localized_country_list
from baseframe.forms import render_form
from coaster.utils import utcnow
from coaster.views import load_models, render_with

from .. import app, lastuser
from ..data import indian_states
from ..extapi import RAZORPAY_PAYMENT_STATUS, razorpay
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
    CURRENCY,
    CURRENCY_SYMBOL,
    LINE_ITEM_STATUS,
    ORDER_STATUS,
    TRANSACTION_TYPE,
    Assignee,
    DiscountCoupon,
    DiscountPolicy,
    Invoice,
    Item,
    ItemCollection,
    LineItem,
    OnlinePayment,
    Order,
    OrderSession,
    PaymentTransaction,
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


def jsonify_line_items(line_items):
    """
    Serialize and return line items.

    Format::

        {
            item_id: {
                'quantity': Y,
                'final_amount': Z,
                'discounted_amount': Z,
                'discount_policy_ids': ['d1', 'd2']
            }
        }
    """
    items_json = {}
    for line_item in line_items:
        item = Item.query.get(line_item.item_id)
        if not items_json.get(str(line_item.item_id)):
            items_json[str(line_item.item_id)] = {
                'is_available': item.is_available,
                'quantity': 0,
                'final_amount': Decimal(0),
                'discounted_amount': Decimal(0),
                'discount_policy_ids': [],
            }
        if line_item.base_amount is not None:
            items_json[str(line_item.item_id)]['base_amount'] = line_item.base_amount
            items_json[str(line_item.item_id)]['final_amount'] += (
                line_item.base_amount - line_item.discounted_amount
            )
            items_json[str(line_item.item_id)][
                'discounted_amount'
            ] += line_item.discounted_amount
        else:
            items_json[str(line_item.item_id)]['final_amount'] = None
            items_json[str(line_item.item_id)]['discounted_amount'] = None
        items_json[str(line_item.item_id)]['quantity'] += 1
        items_json[str(line_item.item_id)][
            'quantity_available'
        ] = item.quantity_available
        if (
            line_item.discount_policy_id
            and line_item.discount_policy_id
            not in items_json[str(line_item.item_id)]['discount_policy_ids']
        ):
            items_json[str(line_item.item_id)]['discount_policy_ids'].append(
                line_item.discount_policy_id
            )
    return items_json


def jsonify_assignee(assignee):
    if assignee:
        return {
            'id': assignee.id,
            'fullname': assignee.fullname,
            'email': assignee.email,
            'phone': assignee.phone,
            'details': assignee.details,
        }


def jsonify_order(data):
    order = data['order']
    line_items = []
    for line_item in order.line_items:
        line_items.append(
            {
                'seq': line_item.line_item_seq,
                'id': line_item.id,
                'title': line_item.item.title,
                'description': line_item.item.description.text,
                'final_amount': line_item.final_amount,
                'assignee_details': line_item.item.assignee_details,
                'assignee': jsonify_assignee(line_item.current_assignee),
                'is_confirmed': line_item.is_confirmed,
                'is_cancelled': line_item.is_cancelled,
                'cancelled_at': json_date_format(line_item.cancelled_at)
                if line_item.cancelled_at
                else "",
                'is_transferable': line_item.is_transferable,
            }
        )
    return jsonify(
        order_id=order.id,
        access_token=order.access_token,
        item_collection_name=order.item_collection.description_text,
        buyer_name=order.buyer_fullname,
        buyer_email=order.buyer_email,
        buyer_phone=order.buyer_phone,
        line_items=line_items,
    )


@app.route('/order/kharcha', methods=['OPTIONS', 'POST'])
@xhr_only
@cors
def kharcha():
    """
    Calculate rates for an order of items and quantities.

    Accepts JSON containing an array of line_items, with the quantity and item_id set
    for each line_item.

    Returns JSON of line items in the format::

        {
            item_id: {
                "quantity": Y,
                "final_amount": Z,
                "discounted_amount": Z,
                "discount_policy_ids": ["d1", "d2"]
            }
        }
    """
    if not request.json or not request.json.get('line_items'):
        return api_error(message='Missing line items', status_code=400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        return api_error(message='Missing line items', status_code=400)

    # Make line item splits and compute amounts and discounts
    line_items = LineItem.calculate(
        [
            {'item_id': li_form.data.get('item_id')}
            for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))
        ],
        coupons=sanitize_coupons(request.json.get('discount_coupons')),
    )
    items_json = jsonify_line_items(line_items)
    order_final_amount = sum(
        [
            values['final_amount']
            for values in items_json.values()
            if values['final_amount'] is not None
        ]
    )
    return jsonify(line_items=items_json, order={'final_amount': order_final_amount})


@app.route('/ic/<item_collection>/order', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((ItemCollection, {'id': 'item_collection'}, 'item_collection'))
def order(item_collection):
    """
    Create an order.

    Accepts JSON containing an array of line_items with the quantity and item_id
    set for each item, and a buyer hash containing `email`, `fullname` and `phone`.

    Creates a purchase order, and returns a JSON containing the final_amount, order id
    and the URL to be used to register a payment against the order.
    """
    if not request.json or not request.json.get('line_items'):
        return api_error(message="Missing line items", status_code=400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        return api_error(message="Invalid line items", status_code=400)
    # See comment in LineItemForm about CSRF
    buyer_form = BuyerForm.from_json(request.json.get('buyer'), meta={'csrf': False})
    if not buyer_form.validate():
        return api_error(
            message="Invalid buyer details", status_code=400, errors=buyer_form.errors
        )

    invalid_quantity_error_msg = _(
        "Selected quantity for ‘{item}’ is not available. Please edit the order and"
        " update the quantity"
    )
    item_dicts = Item.get_availability(
        [line_item_form.data.get('item_id') for line_item_form in line_item_forms]
    )

    for line_item_form in line_item_forms:
        title_quantity_count = item_dicts.get(line_item_form.data.get('item_id'))
        if title_quantity_count:
            item_title, item_quantity_total, line_item_count = title_quantity_count
            if (
                line_item_count + line_item_form.data.get('quantity')
            ) > item_quantity_total:
                return api_error(
                    message=invalid_quantity_error_msg.format(item=item_title),
                    status_code=400,
                    errors=['order calculation error'],
                )
        else:
            item = Item.query.get(line_item_form.data.get('item_id'))
            if line_item_form.data.get('quantity') > item.quantity_total:
                return api_error(
                    message=invalid_quantity_error_msg.format(item=item.title),
                    status_code=400,
                    errors=['order calculation error'],
                )

    user = User.query.filter_by(email=buyer_form.email.data).first()
    order = Order(
        user=user,
        organization=item_collection.organization,
        item_collection=item_collection,
        buyer_email=buyer_form.email.data,
        buyer_fullname=buyer_form.fullname.data,
        buyer_phone=buyer_form.phone.data,
    )

    sanitized_coupon_codes = sanitize_coupons(request.json.get('discount_coupons'))
    line_item_tups = LineItem.calculate(
        [
            {'item_id': li_form.data.get('item_id')}
            for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))
        ],
        coupons=sanitized_coupon_codes,
    )

    for idx, line_item_tup in enumerate(line_item_tups):
        item = Item.query.get(line_item_tup.item_id)

        if item.restricted_entry:
            if not sanitized_coupon_codes or not DiscountPolicy.is_valid_access_coupon(
                item, sanitized_coupon_codes
            ):
                # Skip adding a restricted item to the cart without the proper access code
                break

        if item.is_available:
            if line_item_tup.discount_policy_id:
                policy = DiscountPolicy.query.get(line_item_tup.discount_policy_id)
            else:
                policy = None
            if line_item_tup.discount_coupon_id:
                coupon = DiscountCoupon.query.get(line_item_tup.discount_coupon_id)
            else:
                coupon = None

            line_item = LineItem(
                order=order,
                item=item,
                discount_policy=policy,
                line_item_seq=idx + 1,
                discount_coupon=coupon,
                ordered_at=utcnow(),
                base_amount=line_item_tup.base_amount,
                discounted_amount=line_item_tup.discounted_amount,
                final_amount=line_item_tup.base_amount
                - line_item_tup.discounted_amount,
            )
            db.session.add(line_item)
        else:
            return api_error(
                message=_("‘{item}’ is no longer available.").format(item=item.title),
                status_code=400,
                errors=['order calculation error'],
            )

    db.session.add(order)

    if request.json.get('order_session'):
        order_session_form = OrderSessionForm.from_json(
            request.json.get('order_session'), meta={'csrf': False}
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
            'payment_url': url_for('payment', order=order.id),
            'free_order_url': url_for('free', order=order.id),
            'final_amount': order.get_amounts(
                LINE_ITEM_STATUS.PURCHASE_ORDER
            ).final_amount,
        },
        status_code=201,
    )


@app.route('/order/<order>/free', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((Order, {'id': 'order'}, 'order'))
def free(order):
    """Complete a order which has a final_amount of 0."""
    order_amounts = order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER)
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
            subject=_(
                "{item_collection_title}: Your registration is confirmed!"
            ).format(item_collection_title=order.item_collection.title),
            template='free_order_confirmation_mail.html.jinja2',
        )
        return api_success(
            result={'order_id': order.id},
            doc=_("Free order confirmed"),
            status_code=201,
        )

    else:
        return api_error(message="Free order confirmation failed", status_code=402)


@app.route('/order/<order>/payment', methods=['GET', 'OPTIONS', 'POST'])
@xhr_only
@cors
@load_models((Order, {'id': 'order'}, 'order'))
def payment(order):
    """
    Capture a payment.

    Accepts JSON containing `pg_paymentid`. Creates a payment object, attempts to
    'capture' the payment from Razorpay, and returns a JSON containing the result of the
    operation.

    A successful capture results in a `payment_transaction` registered against the
    order.
    """
    if not request.json.get('pg_paymentid'):
        return api_error(message="Missing payment id", status_code=400)

    order_amounts = order.get_amounts(LINE_ITEM_STATUS.PURCHASE_ORDER)
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
            currency=CURRENCY.INR,
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
            subject=_(
                "{item_collection_title}: Thank you for your order (#{invoice_no})!"
            ).format(
                item_collection_title=order.item_collection.title,
                invoice_no=order.invoice_no,
            ),
        )
        return api_success(
            result={'invoice_id': invoice.id},
            doc=_("Payment verified"),
            status_code=201,
        )
    else:
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
def receipt(order):
    if not order.is_confirmed:
        abort(404)
    line_items = LineItem.query.filter(
        LineItem.order == order, LineItem.status.in_([LINE_ITEM_STATUS.CONFIRMED])
    ).all()
    return render_template(
        'cash_receipt.html.jinja2',
        order=order,
        org=order.organization,
        line_items=line_items,
        currency_symbol=CURRENCY_SYMBOL['INR'],
    )


def jsonify_invoice(invoice):
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
def edit_invoice_details(order):
    """Update invoice with buyer's address and taxid."""
    if not order.is_confirmed:
        abort(404)
    invoice_dict = request.json.get('invoice')
    if not request.json or not invoice_dict:
        return api_error(message=_("Missing invoice details"), status_code=400)

    invoice = Invoice.query.get(request.json.get('invoice_id'))
    if invoice.is_final:
        return api_error(
            message=_("This invoice has been finalised and hence cannot be modified"),
            status_code=400,
        )

    invoice_form = InvoiceForm.from_json(invoice_dict, meta={'csrf': False})
    if not invoice_form.validate():
        return api_error(
            message=_("Incorrect invoice details"),
            status_code=400,
            errors=invoice_form.errors,
        )
    else:
        invoice_form.populate_obj(invoice)
        db.session.commit()
        return api_success(
            result={'message': 'Invoice updated', 'invoice': jsonify_invoice(invoice)},
            doc=_("Invoice details added"),
            status_code=201,
        )


def jsonify_invoices(data_dict):
    invoices_list = []
    for invoice in data_dict['invoices']:
        invoices_list.append(jsonify_invoice(invoice))
    return jsonify(
        invoices=invoices_list,
        access_token=data_dict['order'].access_token,
        states=[
            {'name': state['name'], 'code': state['short_code_text']}
            for state in sorted(indian_states, key=lambda k: k['name'])
        ],
        countries=[
            {'name': name, 'code': code} for code, name in localized_country_list()
        ],
    )


@app.route('/order/<access_token>/invoice', methods=['GET'])
@render_with(
    {'text/html': 'invoice_form.html.jinja2', 'application/json': jsonify_invoices}
)
@load_models((Order, {'access_token': 'access_token'}, 'order'))
def invoice_details_form(order):
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
def line_items(order):
    return {'order': order, 'org': order.organization}


def jsonify_orders(orders):
    api_orders = []

    def format_assignee(line_item):
        if not line_item.current_assignee:
            return {}
        assignee = {
            'fullname': line_item.current_assignee.fullname,
            'email': line_item.current_assignee.email,
            'phone': line_item.current_assignee.phone,
        }

        for key in line_item.item.assignee_details:
            assignee[key] = line_item.current_assignee.details.get(key)
        return assignee

    for order in orders:
        order_dict = {'invoice_no': order.invoice_no, 'line_items': []}
        for line_item in order.line_items:
            order_dict['line_items'].append(
                {
                    'assignee': format_assignee(line_item),
                    'line_item_seq': line_item.line_item_seq,
                    'line_item_status': "confirmed"
                    if line_item.is_confirmed
                    else "cancelled",
                    'item': {'title': line_item.item.title},
                }
            )
        api_orders.append(order_dict)
    return api_orders


def get_coupon_codes_from_line_items(line_items):
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
    order, original_line_item, updated_line_item_tup, line_item_seq
):
    """Update a line item by marking the original as void and creating a replacement."""
    original_line_item.make_void()
    item = Item.query.get(updated_line_item_tup.item_id)
    if updated_line_item_tup.discount_policy_id:
        policy = DiscountPolicy.query.get(updated_line_item_tup.discount_policy_id)
    else:
        policy = None
    if updated_line_item_tup.discount_coupon_id:
        coupon = DiscountCoupon.query.get(updated_line_item_tup.discount_coupon_id)
    else:
        coupon = None

    return LineItem(
        order=order,
        item=item,
        discount_policy=policy,
        previous=original_line_item,
        status=LINE_ITEM_STATUS.CONFIRMED,
        line_item_seq=line_item_seq,
        discount_coupon=coupon,
        ordered_at=utcnow(),
        base_amount=updated_line_item_tup.base_amount,
        discounted_amount=updated_line_item_tup.discounted_amount,
        final_amount=updated_line_item_tup.base_amount
        - updated_line_item_tup.discounted_amount,
    )


def update_order_on_line_item_cancellation(
    order, pre_cancellation_line_items, cancelled_line_item
):
    """Cancel the given line item and updates the order."""
    active_line_items = [
        pre_cancellation_line_item
        for pre_cancellation_line_item in pre_cancellation_line_items
        if pre_cancellation_line_item != cancelled_line_item
    ]
    recalculated_line_item_tups = LineItem.calculate(
        active_line_items,
        recalculate=True,
        coupons=get_coupon_codes_from_line_items(active_line_items),
    )

    last_line_item_seq = LineItem.get_max_seq(order)
    for idx, line_item_tup in enumerate(
        recalculated_line_item_tups, start=last_line_item_seq + 1
    ):
        # Fetch the line item object
        pre_cancellation_line_item = [
            pre_cancellation_line_item
            for pre_cancellation_line_item in pre_cancellation_line_items
            if pre_cancellation_line_item.id == line_item_tup.id
        ][0]
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


def process_line_item_cancellation(line_item):
    order = line_item.order
    # initialize refund_amount to 0
    refund_amount = Decimal(0)

    if (not line_item.is_free) and order.net_amount > Decimal('0'):
        if line_item.discount_policy:
            pre_cancellation_order_amount = (
                order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).confirmed_amount
                - order.refunded_amount
            )
            pre_cancellation_line_items = order.confirmed_line_items
            line_item.cancel()
            updated_order = update_order_on_line_item_cancellation(
                order, pre_cancellation_line_items, line_item
            )
            post_cancellation_order_amount = (
                updated_order.get_amounts(LINE_ITEM_STATUS.CONFIRMED).confirmed_amount
                - order.refunded_amount
            )
            refund_amount = (
                pre_cancellation_order_amount - post_cancellation_order_amount
            )
        else:
            line_item.cancel()
            refund_amount = line_item.final_amount

        if refund_amount > order.net_amount:
            # since the refund amount is more than the net amount received
            # only refund the remaining amount
            refund_amount = order.net_amount

    if refund_amount > Decimal('0'):
        payment = OnlinePayment.query.filter_by(
            order=line_item.order, pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED
        ).one()
        rp_resp = razorpay.refund_payment(payment.pg_paymentid, refund_amount)
        rp_refund = rp_resp.json()
        if rp_resp.status_code == 200:
            db.session.add(
                PaymentTransaction(
                    order=order,
                    transaction_type=TRANSACTION_TYPE.REFUND,
                    pg_refundid=rp_refund['id'],
                    online_payment=payment,
                    amount=refund_amount,
                    currency=CURRENCY.INR,
                    refunded_at=func.utcnow(),
                    refund_description=_("Refund: {line_item_title}").format(
                        line_item_title=line_item.item.title
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
def cancel_line_item(line_item):
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


def process_partial_refund_for_order(data_dict):
    order = data_dict['order']
    form = data_dict['form']
    request_method = data_dict['request_method']

    if request_method == 'GET':
        return jsonify(
            form_template=render_form(
                form=form, title="Partial refund", submit="Refund", with_chrome=False
            ).get_data(as_text=True)
        )
    if form.validate_on_submit():
        requested_refund_amount = form.amount.data
        payment = OnlinePayment.query.filter_by(
            order=order, pg_payment_status=RAZORPAY_PAYMENT_STATUS.CAPTURED
        ).one()
        rp_resp = razorpay.refund_payment(payment.pg_paymentid, requested_refund_amount)
        rp_refund = rp_resp.json()
        if rp_resp.status_code == 200:
            transaction = PaymentTransaction(
                order=order,
                transaction_type=TRANSACTION_TYPE.REFUND,
                online_payment=payment,
                currency=CURRENCY.INR,
                pg_refundid=rp_refund['id'],
                refunded_at=func.utcnow(),
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
        else:
            raise PaymentGatewayError(
                _("Refund failed for order #{order}: {msg}").format(
                    order=order.id, msg=rp_refund['error']['description']
                ),
                424,
                _(
                    "Refund failed with “{reason}̦”. Try again, or contact support at"
                    " {email}."
                ).format(
                    reason=rp_refund['error']['description'],
                    email=order.organization.contact_email,
                ),
            )
    else:
        return api_error(message='Invalid input', status_code=403, errors=form.errors)


@app.route('/admin/ic/<ic_id>/order/<order_id>/partial_refund', methods=['GET', 'POST'])
@lastuser.requires_login
@render_with(
    {
        'text/html': 'index.html.jinja2',
        'application/json': process_partial_refund_for_order,
    }
)
@load_models((Order, {'id': 'order_id'}, 'order'), permission='org_admin')
def partial_refund_order(order):
    return {
        'order': order,
        'form': OrderRefundForm(parent=order),
        'request_method': request.method,
    }


@app.route('/api/1/ic/<item_collection>/orders', methods=['GET', 'OPTIONS'])
@load_models((ItemCollection, {'id': 'item_collection'}, 'item_collection'))
def item_collection_orders(item_collection):
    organization = item_collection.organization
    # TODO: Replace with a better authentication system
    if not request.args.get('access_token') or request.args.get(
        'access_token'
    ) != organization.details.get("access_token"):
        abort(401)
    orders = item_collection.orders.filter(
        Order.status.in_([ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE])
    ).all()
    return jsonify(orders=jsonify_orders(orders))
