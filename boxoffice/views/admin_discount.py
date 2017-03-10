# -*- coding: utf-8 -*-

from __future__ import division
import math
from flask import jsonify
from .. import app, lastuser
from coaster.views import load_models, render_with, requestargs
from ..models import db
from boxoffice.models import Organization, DiscountPolicy, DiscountCoupon, Price, CURRENCY_SYMBOL, CURRENCY
from ..forms import DiscountPolicyForm, DiscountCouponForm, DiscountPriceForm, CouponBasedDiscountPolicyForm, AutomaticDiscountPolicyForm, PriceBasedDiscountPolicyForm
from utils import xhr_only, date_time_format, api_error, api_success


def jsonify_price(price):
    if price:
        return {
            'amount': price.amount,
            'start_at': date_time_format(price.start_at),
            'end_at': date_time_format(price.end_at)
        }
    else:
        return None


def jsonify_discount_policy(policy):
    return {
        'id': policy.id,
        'name': policy.name,
        'title': policy.title,
        'discount_type': "Automatic" if policy.is_automatic else "Coupon based",
        'item_quantity_min': policy.item_quantity_min,
        'percentage': policy.percentage,
        'is_price_based': policy.is_price_based,
        'discount_code_base': policy.discount_code_base,
        'bulk_coupon_usage_limit': policy.bulk_coupon_usage_limit,
        'discount': policy.percentage if not policy.is_price_based else '',
        'price_details': jsonify_price(Price.query.filter(Price.discount_policy == policy).first()) if policy.is_price_based else '',
        'currency': CURRENCY_SYMBOL['INR'],
        'dp_items': [{'id': str(item.id), 'title': "{ic_title}: {title}".format(ic_title=item.item_collection.title, title=item.title)} for item in policy.items]
    }


def jsonify_discount_policies(data_dict):
    discount_policies_list = []
    for policy in data_dict['discount_policies']:
        discount_policies_list.append(jsonify_discount_policy(policy))
    return jsonify(
        org_name=data_dict['org'].name, title=data_dict['org'].title,
        discount_policies=discount_policies_list,
        currency=[currency for currency, label in CURRENCY.items()],
        total_pages=data_dict['total_pages'],
        paginated=data_dict['total_pages'] > 1,
        current_page=data_dict['current_page']
    )


@app.route('/admin/o/<org>/discount_policy')
@lastuser.requires_login
@render_with({'text/html': 'index.html', 'application/json': jsonify_discount_policies})
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@requestargs('search', ('page', int), ('size', int))
def admin_discount_policies(organization, search=None, page=1, size=None):
    print 'size', size
    results_per_page = size or 20

    discount_policies = organization.discount_policies

    if search:
        discount_policies = discount_policies.filter(
            DiscountPolicy.title.ilike('%{query}%'.format(query=search)))

    total_policies = discount_policies.count()
    total_pages = int(math.ceil(total_policies / results_per_page))
    offset = (page - 1) * results_per_page

    discount_policies = discount_policies.limit(results_per_page).offset(offset).all()

    return dict(
        org=organization, title=organization.title,
        discount_policies=discount_policies,
        total_pages=total_pages,
        paginated=(total_policies > results_per_page),
        current_page=page)


def make_discount(discount_policy, discount_policy_form, secret=False):
    discount_policy_form.populate_obj(discount_policy)
    if secret:
        discount_policy.set_secret()
    discount_policy.make_name()
    return discount_policy


@app.route('/admin/o/<org>/discount_policy/new', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
def admin_new_discount_policy(organization):
    discount_policy = DiscountPolicy(organization=organization)
    discount_policy_form = DiscountPolicyForm()
    discount_policy_form.populate_obj(discount_policy)

    if discount_policy.is_price_based:
        discount_policy_form = PriceBasedDiscountPolicyForm(parent=discount_policy.organization)
        with db.session.no_autoflush:
            if not discount_policy_form.validate_on_submit():
                return api_error(message=discount_policy_form.errors, status_code=400)
            discount_price_form = DiscountPriceForm(parent=discount_policy)
            if not discount_price_form.validate_on_submit():
                return api_error(message=discount_price_form.errors, status_code=400)
            discount_price = Price(discount_policy=discount_policy)
            discount_price_form.populate_obj(discount_price)
            discount_price.make_name()
        db.session.add(discount_price)
        discount_policy = make_discount(discount_policy, discount_policy_form, secret=True)
        discount_policy.items.append(discount_price.item)
    elif discount_policy.is_coupon:
        discount_policy_form = CouponBasedDiscountPolicyForm(parent=discount_policy.organization)
        with db.session.no_autoflush:
            if not discount_policy_form.validate_on_submit():
                return api_error(message=discount_policy_form.errors, status_code=400)
        discount_policy = make_discount(discount_policy, discount_policy_form, secret=True)
    elif discount_policy.is_automatic:
        discount_policy_form = AutomaticDiscountPolicyForm(parent=discount_policy.organization)
        with db.session.no_autoflush:
            if not discount_policy_form.validate_on_submit():
                return api_error(message=discount_policy_form.errors, status_code=400)
        discount_policy = make_discount(discount_policy, discount_policy_form)
    else:
        return api_error(message="Incorrect discount type", status_code=400)

    db.session.add(discount_policy)
    db.session.commit()
    return api_success(result={'discount_policy': jsonify_discount_policy(discount_policy)},
        doc="New discount policy created.", status_code=201)


@app.route('/admin/discount_policy/<discount_policy_id>/edit', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
def admin_edit_discount_policy(discount_policy):
    if discount_policy.is_price_based:
        discount_policy_form = PriceBasedDiscountPolicyForm(obj=discount_policy, model=DiscountPolicy)
        discount_price = Price.query.filter_by(item=discount_policy.items[0], discount_policy=discount_policy).one()
        discount_price_form = DiscountPriceForm(obj=discount_price, model=Price, parent=discount_policy)
        if not discount_price_form.validate_on_submit():
            return api_error(message=discount_price_form.errors, status_code=400)
        discount_price_form.populate_obj(discount_price)
        if discount_policy.items and discount_price.item is not discount_policy.items[0]:
            discount_policy.items = [discount_price.item]
    elif discount_policy.is_coupon:
        discount_policy_form = CouponBasedDiscountPolicyForm(obj=discount_policy, model=DiscountPolicy)
    elif discount_policy.is_automatic:
        discount_policy_form = AutomaticDiscountPolicyForm(obj=discount_policy, model=DiscountPolicy)
    else:
        return api_error(message="Incorrect discount type", status_code=400)

    if discount_policy_form.validate_on_submit():
        discount_policy_form.populate_obj(discount_policy)
        db.session.commit()
        return api_success(result={'discount_policy': jsonify_discount_policy(discount_policy)}, doc="Discount policy updated.", status_code=200)
    else:
        return api_error(message=discount_policy_form.errors, status_code=400)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons/new', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
def admin_new_coupon(discount_policy):
    coupon_form = DiscountCouponForm()
    coupons = []
    if not coupon_form.validate_on_submit():
        return api_error(message=coupon_form.errors, status_code=400)
    if coupon_form.count.data > 1:
        # Create a signed discount coupon code
        if not discount_policy.secret:
            discount_policy.set_secret()
        for x in range(coupon_form.count.data):
            coupons.append(discount_policy.gen_signed_code())
    else:
        # Create a new discount coupon
        if coupon_form.coupon_code.data:
            # Custom discount code
            coupon = DiscountCoupon(discount_policy=discount_policy,
                usage_limit=coupon_form.usage_limit.data,
                code=coupon_form.coupon_code.data)
        else:
            # Randomly generated discount code
            coupon = DiscountCoupon(discount_policy=discount_policy,
                usage_limit=coupon_form.usage_limit.data)
        db.session.add(coupon)
        db.session.commit()
        coupons.append(coupon.code)
    return api_success(result={'coupons': coupons}, doc="Discount coupon created.", status_code=201)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons')
@lastuser.requires_login
@xhr_only
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
def admin_discount_coupons(discount_policy):
    coupons_list = [{'code': coupon.code, 'usage_limit': coupon.usage_limit, 'available': coupon.usage_limit - coupon.used_count} for coupon in discount_policy.discount_coupons]
    return api_success(result={'coupons': coupons_list}, doc="List of discount coupons", status_code=200)
