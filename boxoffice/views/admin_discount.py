# -*- coding: utf-8 -*-
from __future__ import division
import datetime
import math
from flask import jsonify, make_response, request
from .. import app, lastuser
from coaster.views import load_models, render_with
from ..models import db
from boxoffice.models import Organization, DiscountPolicy, DiscountCoupon, DISCOUNT_TYPE, Item, Price, CURRENCY_SYMBOL
from utils import xhr_only, date_time_format


# Move this to settings maybe
PAGE_SIZE = 6


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
        'secret': policy.secret,
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
    query = request.args.get('search')
    page = request.args.get('page', 1)

    if request.is_xhr:
        if query:
            discount_policies = DiscountPolicy.query.filter(DiscountPolicy.title.ilike('%{query}%'.format(query=query)))
        else:
            discount_policies = DiscountPolicy.query.filter(DiscountPolicy.organization == organization).order_by('created_at desc')

        total_policies = discount_policies.count()

        try:
            page = int(page)
            offset = (page - 1) * PAGE_SIZE
            discount_policies = discount_policies.limit(PAGE_SIZE).offset(offset)
        except ValueError:
            pass

        print page

        return dict(
            org=organization, title=organization.title,
            discount_policies=discount_policies,
            total_pages=int(math.ceil(total_policies/PAGE_SIZE)),
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
    title = request.json.get('title')
    if request.json.get('is_price_based'):
        is_price_based = int(request.json.get('is_price_based'))
    else:
        return make_response(jsonify(status='error', error='missing_details', error_description="Discount type missing"), 400)
    items = request.json.get('items')
    if not items:
        return make_response(jsonify(status='error', error='missing_details', error_description="Discounted ticket missing"), 400)
    if is_price_based:
        discount_policy = DiscountPolicy(title=title, discount_type=DISCOUNT_TYPE.COUPON, is_price_based=True, organization=organization)
        item = Item.query.get(items[0])
        discount_policy.items.append(item)
        db.session.add(discount_policy)
        db.session.commit()
        price_title = request.json.get('price_title')
        start_datetime_string = request.json.get('start_at')
        if start_datetime_string:
            # Fix: Need to change it to utc
            start_at = datetime.datetime.strptime(start_datetime_string, '%d %m %Y %H:%M:%S')
        end_datetime_string = request.json.get('end_at')
        if end_datetime_string:
            # Fix: Need to change it to utc
            end_at = datetime.datetime.strptime(end_datetime_string, '%d %m %Y %H:%M:%S')
        amount = int(request.json.get('amount'))
        item = Item.query.get(items[0])
        discount_price = Price(item=item, discount_policy=discount_policy, title=price_title, start_at=start_at, end_at=end_at, amount=amount)
        db.session.add(discount_price)
        db.session.commit()
    else:
        if request.json.get('discount_type'):
            discount_type = int(request.json.get('discount_type'))
            if request.json.get('percentage'):
                percentage = int(request.json.get('percentage'))
            else:
                return make_response(jsonify(status='error', error='missing_details', error_description="Discount percentage missing"), 400)
            if discount_type:
                discount_policy = DiscountPolicy(title=title, discount_type=DISCOUNT_TYPE.COUPON, percentage=percentage, organization=organization)
            else:
                if request.json.get('item_quantity_min'):
                    item_quantity_min = int(request.json.get('item_quantity_min'))
                    discount_policy = DiscountPolicy(title=title, discount_type=DISCOUNT_TYPE.AUTOMATIC, item_quantity_min=item_quantity_min, percentage=percentage, organization=organization)
                else:
                    return make_response(jsonify(status='error', error='missing_details', error_description="Minimum number of tickets missing"), 400)
            for item_id in items:
                item = Item.query.get(item_id)
                discount_policy.items.append(item)
            db.session.add(discount_policy)
            db.session.commit()
        else:
            return make_response(jsonify(status='error', error='missing_details', error_description="Discount type missing"), 400)
    return make_response(jsonify(status='ok', result={'message': 'New discount policy created', 'discount_policy': jsonify_discount_policy(discount_policy)}), 201)


@app.route('/admin/discount_policy/<discount_policy_id>/edit', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_edit_discount_policy(discount_policy):
    if not request.json:
        return make_response(jsonify(status='error', error='missing_details', error_description="Discount policy details missing"), 400)

    if request.json.get('title'):
        discount_policy.title = request.json.get('title')
    if not discount_policy.is_price_based:
        if request.json.get('percentage'):
            discount_policy.percentage = int(request.json.get('percentage'))
    if discount_policy.is_automatic:
        item_quantity_min = int(request.json.get('item_quantity_min'))
        if item_quantity_min:
            if item_quantity_min >= 1:
                discount_policy.item_quantity_min = item_quantity_min
            else:
               return make_response(jsonify(status='error', error='item_quantity_min_error', error_description="Minimum item quantity cannot be less than one"), 400)
    items = request.json.get('items')
    if items:
        discount_policy.items = []
        for item_id in items:
            item = Item.query.get(item_id)
            discount_policy.items.append(item)
    db.session.add(discount_policy)
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
    coupons = []
    if request.json.get('count'):
        no_of_coupons = int(request.json.get('count'))
    if no_of_coupons > 1:
        for x in range(no_of_coupons):
            # TODO: Create Discount Code Base & secret if not present
            coupon = discount_policy.gen_signed_code()
            coupons.append({'code': coupon})
    else:
        if request.json.get('usage_limit'):
            usage_limit = int(request.json.get('usage_limit'))
        if usage_limit < 1:
            return make_response(jsonify(status='error', error='error_usage_limit', error_description="Discount coupon usage limit cannot be less than 1"), 400)
        else:
            coupon_code = request.json.get('coupon_code')
            if coupon_code:
                coupon = DiscountCoupon(discount_policy=discount_policy, usage_limit=usage_limit, code=coupon_code)
            else:
                coupon = DiscountCoupon(discount_policy=discount_policy, usage_limit=usage_limit)
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
