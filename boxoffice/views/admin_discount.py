from typing import Optional

from flask import jsonify, request

from baseframe import _, forms
from baseframe.forms import render_form
from coaster.views import load_models, render_with, requestargs

from .. import app, lastuser
from ..forms import (
    AutomaticDiscountPolicyForm,
    CouponBasedDiscountPolicyForm,
    DiscountCouponForm,
    DiscountPolicyForm,
    DiscountPriceForm,
    PriceBasedDiscountPolicyForm,
)
from ..models import CURRENCY, DiscountCoupon, DiscountPolicy, Organization, Price, db
from .utils import api_error, api_success, xhr_only


def jsonify_discount_policy(discount_policy: DiscountPolicy):
    details = dict(discount_policy.current_access())
    details['price_details'] = {}
    if discount_policy.is_price_based:
        price = Price.query.filter(Price.discount_policy == discount_policy).first()
        details['price_details'] = dict(price.current_access())
    details['dp_items'] = [
        {
            'id': str(ticket.id),
            'title': f'{ticket.menu.title}: {ticket.title}',
        }
        for ticket in discount_policy.tickets
    ]
    return details


def jsonify_discount_policies(data_dict):
    discount_policies_list = []
    for discount_policy in data_dict['discount_policies']:
        discount_policies_list.append(jsonify_discount_policy(discount_policy))
    return jsonify(
        account_name=data_dict['org'].name,
        account_title=data_dict['org'].title,
        discount_policies=discount_policies_list,
        currency=[currency for currency, label in CURRENCY.items()],
        total_pages=data_dict['total_pages'],
        paginated=data_dict['total_pages'] > 1,
        current_page=data_dict['current_page'],
    )


@app.route('/admin/o/<org>/discount_policy')
@lastuser.requires_login
@render_with(
    {'text/html': 'index.html.jinja2', 'application/json': jsonify_discount_policies}
)
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
@requestargs('search', ('page', int), ('size', int))
def admin_discount_policies(
    organization: Organization, search: Optional[str] = None, page=1, size=None
):
    results_per_page = size or 20

    discount_policies = organization.discount_policies
    if search:
        # FIXME: quote search for LIKE format characters, and don't use LIKE at all
        discount_policies = discount_policies.filter(
            DiscountPolicy.title.ilike(f'%{search}%')
        )
    paginated_discount_policies = discount_policies.paginate(
        page=page, per_page=results_per_page
    )

    return {
        'org': organization,
        'title': organization.title,
        'discount_policies': paginated_discount_policies.items,
        'total_pages': paginated_discount_policies.pages,
        'paginated': (paginated_discount_policies.total > results_per_page),
        'current_page': page,
    }


@app.route('/admin/o/<org>/discount_policy/new', methods=['POST'])
@lastuser.requires_login
@xhr_only
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def admin_new_discount_policy(organization: Organization):
    discount_policy = DiscountPolicy(organization=organization)
    discount_policy_form = DiscountPolicyForm(model=DiscountPolicy)
    discount_policy_form.populate_obj(discount_policy)
    discount_policy_error_msg = _(
        "The discount could not be created. Please rectify the indicated issues"
    )

    if discount_policy.is_price_based:
        discount_policy_form = PriceBasedDiscountPolicyForm(
            model=DiscountPolicy, parent=discount_policy.organization
        )
        with db.session.no_autoflush:
            if not discount_policy_form.validate_on_submit():
                return api_error(
                    message=discount_policy_error_msg,
                    status_code=400,
                    errors=discount_policy_form.errors,
                )
            discount_policy_form.populate_obj(discount_policy)
            discount_policy.make_name()
            discount_price_form = DiscountPriceForm(model=Price, parent=discount_policy)
            if not discount_price_form.validate_on_submit():
                return api_error(
                    message=_(
                        "There was an issue with the price. Please rectify the"
                        " indicated issues"
                    ),
                    status_code=400,
                    errors=discount_price_form.errors,
                )
            discount_price = Price(discount_policy=discount_policy)
            discount_price_form.populate_obj(discount_price)
            discount_price.make_name()
        db.session.add(discount_price)
        discount_policy.tickets.append(discount_price.ticket)
    elif discount_policy.is_coupon:
        discount_policy_form = CouponBasedDiscountPolicyForm(
            model=DiscountPolicy, parent=discount_policy.organization
        )
        with db.session.no_autoflush:
            if not discount_policy_form.validate_on_submit():
                return api_error(
                    message=discount_policy_error_msg,
                    status_code=400,
                    errors=discount_policy_form.errors,
                )
        discount_policy_form.populate_obj(discount_policy)
        discount_policy.make_name()
    elif discount_policy.is_automatic:
        discount_policy_form = AutomaticDiscountPolicyForm(
            model=DiscountPolicy, parent=discount_policy.organization
        )
        with db.session.no_autoflush:
            if not discount_policy_form.validate_on_submit():
                return api_error(
                    message=discount_policy_error_msg,
                    status_code=400,
                    errors=discount_policy_form.errors,
                )
        discount_policy_form.populate_obj(discount_policy)
        discount_policy.make_name()
    else:
        return api_error(message=_("Incorrect discount type"), status_code=400)

    db.session.add(discount_policy)
    db.session.commit()
    return api_success(
        result={'discount_policy': jsonify_discount_policy(discount_policy)},
        doc=_("New discount policy created"),
        status_code=201,
    )


@app.route('/admin/discount_policy/<discount_policy_id>/edit', methods=['POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_edit_discount_policy(discount_policy: DiscountPolicy):
    discount_policy_error_msg = _(
        "The discount could not be updated. Please rectify the indicated issues"
    )
    if discount_policy.is_price_based and discount_policy.tickets:
        discount_policy_form = PriceBasedDiscountPolicyForm(
            obj=discount_policy, model=DiscountPolicy
        )
        discount_price = Price.query.filter_by(
            ticket=discount_policy.tickets[0], discount_policy=discount_policy
        ).one()
        discount_price_form = DiscountPriceForm(
            obj=discount_price, model=Price, parent=discount_policy
        )
        if not discount_price_form.validate_on_submit():
            return api_error(
                message=_(
                    "There was an issue with the price. Please rectify the indicated"
                    " issues"
                ),
                status_code=400,
                errors=discount_price_form.errors,
            )
        discount_price_form.populate_obj(discount_price)
        if (
            discount_policy.tickets
            and discount_price.ticket is not discount_policy.tickets[0]
        ):
            discount_policy.tickets = [discount_price.ticket]
    elif discount_policy.is_coupon:
        discount_policy_form = CouponBasedDiscountPolicyForm(
            obj=discount_policy,
            parent=discount_policy.organization,
            model=DiscountPolicy,
        )
    elif discount_policy.is_automatic:
        discount_policy_form = AutomaticDiscountPolicyForm(
            obj=discount_policy, model=DiscountPolicy
        )
    else:
        return api_error(message=_("Incorrect discount type"), status_code=400)

    if discount_policy_form.validate_on_submit():
        discount_policy_form.populate_obj(discount_policy)
        db.session.commit()
        return api_success(
            result={'discount_policy': jsonify_discount_policy(discount_policy)},
            doc=_("Discount policy updated"),
            status_code=200,
        )
    return api_error(
        message=discount_policy_error_msg,
        status_code=400,
        errors=discount_policy_form.errors,
    )


@app.route(
    '/admin/o/<org_name>/discount_policy/<discount_policy_id>/delete',
    methods=['GET', 'POST'],
)
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_delete_discount_policy(discount_policy: DiscountPolicy):
    form = forms.Form()
    if request.method == 'GET':
        return jsonify(
            form_template=render_form(
                form=form,
                title="Delete discount policy",
                submit="Delete",
                with_chrome=False,
            ).get_data(as_text=True)
        )

    if not form.validate_on_submit():
        return api_error(
            message=_("The discount policy could not be deleted."),
            status_code=400,
            errors=form.errors,
        )

    db.session.delete(discount_policy)
    db.session.commit()
    return api_success(result={}, doc="Discount policy deleted.", status_code=200)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons/new', methods=['POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_new_coupon(discount_policy: DiscountPolicy):
    coupon_form = DiscountCouponForm(parent=discount_policy)

    if not coupon_form.validate_on_submit():
        return api_error(
            message=_(
                "The coupon could not be created. Please rectify the indicated issues"
            ),
            status_code=400,
            errors=coupon_form.errors,
        )
    if coupon_form.count.data > 1:
        # Create a signed discount coupon code
        # No need to store these coupon codes since they are signed
        coupons = [
            discount_policy.gen_signed_code() for _x in range(coupon_form.count.data)
        ]
    else:
        coupon = DiscountCoupon(discount_policy=discount_policy)
        coupon_form.populate_obj(coupon)
        db.session.add(coupon)
        db.session.commit()
        coupons = [coupon.code]
    return api_success(
        result={'coupons': coupons}, doc=_("Discount coupon created"), status_code=201
    )


@app.route('/admin/discount_policy/<discount_policy_id>/coupons')
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_discount_coupons(discount_policy: DiscountPolicy):
    coupons_list = [
        {
            'code': coupon.code,
            'usage_limit': coupon.usage_limit,
            'available': coupon.usage_limit - coupon.used_count,
        }
        for coupon in discount_policy.discount_coupons
    ]
    return api_success(
        result={'coupons': coupons_list},
        doc=_("List of discount coupons"),
        status_code=200,
    )
