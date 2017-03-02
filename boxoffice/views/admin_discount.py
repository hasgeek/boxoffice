# -*- coding: utf-8 -*-

from __future__ import division
import math
from flask import jsonify, request
from .. import app, lastuser
from coaster.views import load_models, render_with, requestargs
from ..models import db
from boxoffice.models import Organization, ItemCollection, DiscountPolicy, DiscountCoupon, Item, Price, CURRENCY_SYMBOL, CURRENCY
from ..forms import DiscountPolicyForm, DiscountCouponForm, DiscountPriceForm
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
        'dp_items': [{'id': str(item.id), 'title': item.title} for item in policy.items]
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
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_discount_policies}, json=True)
@requestargs('search', ('page', int))
def admin_discount_policies(organization, search=None, page=1):
    results_per_page = 20

    if request.is_xhr:
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
    else:
        return dict(title=organization.title)


@app.route('/admin/o/<org>/discount_policy/new', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@xhr_only
def admin_add_discount_policy(organization):
    discount_policy_form = DiscountPolicyForm(request.form)
    all_items = Item.query.join(ItemCollection).filter(
        ItemCollection.organization == organization).options(db.load_only('id')).all()
    discount_policy_form.items.query = all_items
    if not discount_policy_form.validate_on_submit():
        return api_error(message=discount_policy_form.errors, status_code=400)

    discount_policy = DiscountPolicy(organization=organization)
    if discount_policy_form.discount_type.data:
        discount_policy.set_secret()
    if not discount_policy_form.is_price_based.data:
        discount_policy.items.extend(discount_policy_form.items.data)
    else:
        discount_price_form = DiscountPriceForm(request.form)
        discount_price_form.item.query = all_items
        if not discount_price_form.validate_on_submit():
            return api_error(message=discount_price_form.errors, status_code=400)
    discount_policy_form.populate_obj(discount_policy)
    discount_policy.make_name()
    db.session.add(discount_policy)
    db.session.commit()

    if discount_policy.is_price_based:
        discount_price = Price(discount_policy=discount_policy)
        discount_price_form.populate_obj(discount_price)
        discount_price.make_name()
        db.session.add(discount_price)
        discount_policy.items.append(discount_price.item)
        db.session.commit()
    return api_success(result={'discount_policy': jsonify_discount_policy(discount_policy)},
        doc="New discount policy created.", status_code=200)


@app.route('/admin/o/<org>/discount_policy/<discount_policy_id>/edit', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_edit_discount_policy(organization, discount_policy):
    discount_policy_form = DiscountPolicyForm(request.form)
    all_items = Item.query.join(ItemCollection).filter(
        ItemCollection.organization == organization).options(db.load_only('id')).all()
    discount_policy_form.items.query = all_items

    if not discount_policy_form.validate_on_submit():
        return api_error(message=discount_policy_form.errors, status_code=400)

    if not discount_policy.is_price_based:
        discount_policy.items.extend(discount_policy_form.items.data)
        discount_policy_form.populate_obj(discount_policy)
    else:
        discount_price_form = DiscountPriceForm(request.form)
        discount_price_form.item.query = all_items
        if not discount_price_form.validate_on_submit():
            return api_error(message=discount_price_form.errors, status_code=400)
        discount_price = Price.query.filter_by(discount_policy=discount_policy).one_or_none()
        if discount_price:
            discount_price_form.populate_obj(discount_price)
            db.session.commit()
            discount_policy_form.populate_obj(discount_policy)
            discount_policy.items.append(discount_price.item)
    db.session.commit()
    return api_success(result={'discount_policy': jsonify_discount_policy(discount_policy)}, doc="Discount policy updated.", status_code=200)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons/new', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_create_coupon(discount_policy):
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
    return api_success(result={'coupons': coupons}, doc="Discount coupon created.", status_code=200)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons')
@lastuser.requires_login
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_discount_coupons(discount_policy):
    coupons_list = [{'code': coupon.code, 'usage_limit': coupon.usage_limit, 'available': coupon.usage_limit - coupon.used_count} for coupon in discount_policy.discount_coupons]
    return api_success(result={'coupons': coupons_list}, doc="List of discount coupons", status_code=200)
