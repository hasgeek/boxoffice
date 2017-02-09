# -*- coding: utf-8 -*-
from __future__ import division
import math
from flask import jsonify, make_response, request
from .. import app, lastuser
from coaster.views import load_models, render_with
from coaster.utils import buid
from ..models import db
from boxoffice.models import Organization, DiscountPolicy, DiscountCoupon, Item, Price, CURRENCY_SYMBOL
from ..forms import DiscountForm, DiscountCouponForm
from utils import xhr_only, date_time_format


def jsonify_price(price):
    if price:
        return {
            'price_title': price.title,
            'amount': price.amount,
            'start_at': date_time_format(price.start_at),
            'end_at': date_time_format(price.end_at)
        }
    else:
        return None


def jsonify_discount_policy(policy):
    return {
        'id': policy.id,
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
        total_pages=data_dict['total_pages'],
        paginated=data_dict['total_pages'] > 1,
        current_page=data_dict['current_page']
    )


@app.route('/admin/o/<org>/discount_policies')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_discount_policies}, json=True)
def admin_discount_policies(organization):
    RESULTS_PER_PAGE = 6
    search_query = request.args.get('search')
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.is_xhr:
        discount_policies = organization.discount_policies

        if search_query:
            discount_policies = discount_policies.filter(
                DiscountPolicy.title.ilike('%{query}%'.format(query=search_query))
            )

        total_policies = len(discount_policies)
        total_pages = int(math.ceil(total_policies/RESULTS_PER_PAGE))
        offset = (page - 1) * RESULTS_PER_PAGE
        discount_policies = discount_policies[offset:RESULTS_PER_PAGE+offset]

        return dict(
            org=organization, title=organization.title,
            discount_policies=discount_policies,
            total_pages=total_pages,
            paginated=(total_policies > RESULTS_PER_PAGE),
            current_page=page
        )
    else:
        return dict(
            org=organization, title=organization.title
        )


@app.route('/admin/o/<org>/discount_policy/new', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@xhr_only
def admin_add_discount_policy(organization):
    discount_policy_form = DiscountForm()
    discount_policy_form.items.query = Item.query.all()
    if not discount_policy_form.validate_on_submit():
        return make_response(jsonify(status='error', error='invalid_details', error_description='Invalid details'), 400)
    discount_policy = DiscountPolicy(title=discount_policy_form.title.data, organization=organization)
    discount_policy_form.populate_obj(discount_policy)
    items = request.form.getlist('items')
    for item_id in items:
        item = Item.query.get(item_id)
        discount_policy.items.append(item)
    if discount_policy_form.discount_type.data:
        discount_policy.secret = buid()
    else:
        discount_policy_form.discount_code_base.data = None
    db.session.add(discount_policy)
    db.session.commit()
    if discount_policy_form.is_price_based.data:
        item = Item.query.get(items[0])
        discount_price = Price(discount_policy=discount_policy, title=discount_policy_form.price_title.data, start_at=discount_policy_form.start_at.data, end_at=discount_policy_form.end_at.data, amount=discount_policy_form.amount.data, item=item)
        db.session.add(discount_price)
        db.session.commit()
    return make_response(jsonify(status='ok', result={'message': 'New discount policy created', 'discount_policy': jsonify_discount_policy(discount_policy)}), 201)


@app.route('/admin/discount_policy/<discount_policy_id>/edit', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_edit_discount_policy(discount_policy):
    discount_policy_form = DiscountForm()
    discount_policy_form.items.query = Item.query.all()
    if not discount_policy_form.validate_on_submit():
        return make_response(jsonify(status='error', error='invalid_details', error_description='Invalid details'), 400)
    if not discount_policy_form.discount_type.data:
        discount_policy_form.discount_code_base.data = None
    discount_policy_form.populate_obj(discount_policy)
    items = request.form.getlist('items')
    for item_id in items:
        item = Item.query.get(item_id)
        discount_policy.items.append(item)
    db.session.add(discount_policy)
    db.session.commit()
    if discount_policy_form.is_price_based.data:
        discount_price = Price.query.filter_by(discount_policy=discount_policy).first()
        discount_price.start_at = discount_policy_form.start_at.data
        discount_price.end_at = discount_policy_form.end_at.data
        discount_price.amount = discount_policy_form.amount.data
        db.session.add(discount_price)
        db.session.commit()
    return make_response(jsonify(status='ok', result={'message': 'Discount policy updated', 'discount_policy': jsonify_discount_policy(discount_policy)}), 201)


@app.route('/admin/discount_policy/<discount_policy_id>/generate_coupon', methods=['OPTIONS', 'POST'])
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
        return make_response(jsonify(status='error', error='invalid_details', error_description='Invalid details'), 400)
    if coupon_form.count.data > 1:
        for x in range(coupon_form.count.data):
            if not discount_policy.secret:
                discount_policy.secret = buid()
            coupon = discount_policy.gen_signed_code()
            coupons.append({'code': coupon})
    else:
            if coupon_form.coupon_code.data:
                coupon = DiscountCoupon(discount_policy=discount_policy, usage_limit=coupon_form.usage_limit.data, code=coupon_form.coupon_code.data)
            else:
                coupon = DiscountCoupon(discount_policy=discount_policy, usage_limit=coupon_form.usage_limit.data)
            db.session.add(coupon)
            db.session.commit()
            coupons.append({'code': coupon.code, 'usage_limit': coupon.usage_limit})
    return make_response(jsonify(status='ok', result={'message': 'Discount coupon created', 'coupons': coupons}), 201)


@app.route('/admin/discount_policy/<discount_policy_id>/coupons')
@lastuser.requires_login
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_discount_coupons(discount_policy):
    discount_coupons = DiscountCoupon.query.filter(DiscountCoupon.discount_policy == discount_policy).all()
    coupons_list = []
    for coupon in discount_coupons:
        coupons_list.append({'code': coupon.code, 'usage_limit': coupon.usage_limit, 'available': coupon.usage_limit - coupon.used_count})
    return make_response(jsonify(status='ok', result={'message': 'Discount coupons', 'coupons': coupons_list}), 201)