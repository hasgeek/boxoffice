"""Organization level discount policy management views."""

from typing import TYPE_CHECKING, Any

from flask import Response, render_template, request
from flask.typing import ResponseReturnValue

from baseframe import _, forms
from baseframe.forms import render_form
from coaster.views import load_models, requestargs

from .. import app, lastuser
from ..forms import (
    AutomaticDiscountPolicyForm,
    CouponBasedDiscountPolicyForm,
    DiscountCouponForm,
    DiscountPolicyForm,
    DiscountPriceForm,
    PriceBasedDiscountPolicyForm,
)
from ..models import (
    CurrencyEnum,
    DiscountCoupon,
    DiscountPolicy,
    Organization,
    Price,
    db,
)
from .utils import api_error, api_success, request_wants_json, xhr_only


# TODO: Return TypedDict
def jsonify_discount_policy(discount_policy: DiscountPolicy) -> dict[str, Any]:
    details = dict(discount_policy.current_access())
    details['price_details'] = {}
    if discount_policy.is_price_based:
        price = Price.query.filter(Price.discount_policy == discount_policy).one()
        details['price_details'] = dict(price.current_access())
    details['dp_items'] = [
        {
            'id': str(ticket.id),
            'title': f'{ticket.menu.title}: {ticket.title}',
        }
        for ticket in discount_policy.tickets
    ]
    return details


@app.route('/admin/o/<org>/discount_policy')
@lastuser.requires_login
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
@requestargs('search', ('page', int), ('size', int))
def admin_discount_policies(
    organization: Organization,
    search: str | None = None,
    page: int = 1,
    size: int | None = None,
) -> ResponseReturnValue:
    results_per_page = size or 20

    discount_policies = organization.discount_policies
    if search:
        # FIXME: quote search for LIKE format characters, and don't use LIKE at all
        discount_policies = discount_policies.filter(
            DiscountPolicy.title.ilike(f'%{search}%')
        )
    paginated_discount_policies = discount_policies.paginate(
        page=page, per_page=results_per_page, count=True
    )
    if TYPE_CHECKING:
        assert paginated_discount_policies.total is not None  # nosec B101

    if not request_wants_json():
        return render_template('index.html.jinja2', title=organization.title)
    return {
        'account_name': organization.name,
        'account_title': organization.title,
        'discount_policies': [
            jsonify_discount_policy(discount_policy)
            for discount_policy in paginated_discount_policies.items
        ],
        'currency': [e.value for e in CurrencyEnum],
        'total_pages': paginated_discount_policies.pages,
        'paginated': paginated_discount_policies.pages > 1,
        'current_page': page,
    }


@app.route('/admin/o/<org>/discount_policy/new', methods=['POST'])
@lastuser.requires_login
@xhr_only
@load_models((Organization, {'name': 'org'}, 'organization'), permission='org_admin')
def admin_new_discount_policy(organization: Organization) -> Response:
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
    (DiscountPolicy, {'uuid_hex': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_edit_discount_policy(discount_policy: DiscountPolicy) -> Response:
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
        # FIXME: What's happening here? It's creating a Price object and associating it
        # with which ticket? What if the policy applies to multiple tickets?
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
    (DiscountPolicy, {'uuid_hex': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_delete_discount_policy(
    discount_policy: DiscountPolicy,
) -> ResponseReturnValue:
    form = forms.Form()
    if request.method == 'GET':
        return {
            'form_template': render_form(
                form=form,
                title=_("Delete discount policy"),
                submit=_("Delete"),
                with_chrome=False,
            ).get_data(as_text=True)
        }

    if not form.validate_on_submit():
        return api_error(
            message=_("The discount policy could not be deleted."),
            status_code=400,
            errors=form.errors,
        )

    db.session.delete(discount_policy)
    db.session.commit()
    return api_success(result={}, doc=_("Discount policy deleted."), status_code=200)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons/new', methods=['POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'uuid_hex': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin',
)
def admin_new_coupon(discount_policy: DiscountPolicy) -> Response:
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
def admin_discount_coupons(discount_policy: DiscountPolicy) -> Response:
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
