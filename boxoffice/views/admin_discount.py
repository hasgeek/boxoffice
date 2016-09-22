# -*- coding: utf-8 -*-

import datetime
from flask import jsonify, make_response, request
from .. import app, lastuser
from coaster.views import load_models, render_with
from ..models import db
from boxoffice.models import Organization, DiscountPolicy, DiscountCoupon, Item, Price, CURRENCY_SYMBOL, LineItem
from utils import xhr_only, date_time_format


def jsonify_price(price):
    return {
        'price_title': price.title,
        'amount': price.amount,
        'start_at': date_time_format(price.start_at),
        'end_at': date_time_format(price.end_at)
    }


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
    return jsonify(org_name=data_dict['org'].name, title=data_dict['org'].title, discount_policies=discount_policies_list)


def format_line_items(line_items):
    line_items_list = []
    for line_item in line_items:
        line_items_list.append({
            'item_title': line_item.item.title,
            'fullname': line_item.order.buyer_fullname,
            'email': line_item.order.buyer_email,
            'invoice_no': line_item.order.invoice_no
            })
    return line_items_list


def format_coupons(coupon):
    if coupon.discount_policy.is_coupon:
        return {
            'id': coupon.id,
            'code': coupon.code,
            'usage_limit': coupon.usage_limit,
            'available': coupon.usage_limit - coupon.used_count,
            'discount_policy_title': coupon.discount_policy.title,
            'is_price_based': coupon.discount_policy.is_price_based,
            'currency': CURRENCY_SYMBOL['INR'],
            'discount': Price.query.filter(Price.discount_policy == coupon.discount_policy).first().amount if coupon.discount_policy.is_price_based else coupon.discount_policy.percentage,
            }


def jsonify_discount_coupons(data_dict):
    coupons_list = []
    discount_policies = DiscountPolicy.query.filter(DiscountPolicy.organization == data_dict['org']).all()
    for discount_policy in discount_policies:
        discount_coupons = DiscountCoupon.query.filter(DiscountCoupon.discount_policy == discount_policy).all()
        for coupon in discount_coupons:
            coupons_list.append(format_coupons(coupon))
    coupons = DiscountCoupon().paginate(1, 3, False).items
    return jsonify(org_name=data_dict['org'].name, title=data_dict['org'].title, coupons=coupons_list)


@app.route('/admin/o/<org>/discount_policies')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_discount_policies}, json=True)
def admin_discount_policies(organization):
    discount_policies = DiscountPolicy.query.filter(DiscountPolicy.organization == organization).order_by('created_at desc').all()
    return dict(title=organization.title, org=organization, discount_policies=discount_policies)


@app.route('/admin/o/<org>/discount_policy/new', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@xhr_only
def admin_add_discount_policy(organization):
    title = request.json.get('title')
    discount_type = int(request.json.get('discount_type'))
    items = request.json.get('items')
    discount_code_base = request.json.get('discount_code_base')
    secret = request.json.get('secret')
    if request.json.get('percentage'):
        percentage = int(request.json.get('percentage'))
        discount_policy = DiscountPolicy(title=title, discount_type=discount_type, percentage=percentage, discount_code_base=discount_code_base, secret=secret, organization=organization)
        for item_id in items:
            item = Item.query.get(item_id)
            discount_policy.items.append(item)
        db.session.add(discount_policy)
        db.session.commit()
    else:
        if request.json.get('is_price_based'):
            discount_policy = DiscountPolicy(title=title, discount_type=discount_type, is_price_based=True, organization=organization)
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
    return make_response(jsonify(status='ok', result={'message': 'New discount policy created'}), 201)


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


@app.route('/admin/discount_policy/<discount_policy_id>/coupon', methods=['OPTIONS', 'POST'])
@lastuser.requires_login
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_create_coupon(discount_policy):
    no_of_coupons = int(request.json.get('count'))
    coupons = []
    if request.json.get('usage_limit'):
        usage_limit = int(request.json.get('usage_limit'))
        if usage_limit < 1:
            return make_response(jsonify(status='error', error='error_usage_limit', error_description="Discount coupon usage limit cannot be less than 1"), 400)
        else:
            for x in range(no_of_coupons):
                coupon = DiscountCoupon(discount_policy=discount_policy, usage_limit=usage_limit)
                db.session.add(coupon)
                db.session.commit()
                coupons.append({'code': coupon.code, 'usage_limit': coupon.usage_limit})
    else:
        # TODO: Check if the discount policy can generate signed code
        for x in range(no_of_coupons):
            coupon = discount_policy.gen_signed_code()
            coupons.append({'code': coupon})
    return make_response(jsonify(status='ok', result={'message': 'Discount coupon created', 'coupons': coupons}), 201)


@app.route('/admin/o/<org>/coupons')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_discount_coupons}, json=True)
def admin_discount_coupons(organization):
    return dict(title=organization.title, org=organization)


@app.route('/admin/o/<org>/<coupon>')
@lastuser.requires_login
@load_models(
    (DiscountCoupon, {'id': 'coupon'}, 'coupon')
    )
@xhr_only
def admin_discount_coupon(coupon):
    line_items = LineItem.query.filter(LineItem.discount_coupon == coupon).all()
    return make_response(jsonify(line_items=format_line_items(line_items)))
