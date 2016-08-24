# -*- coding: utf-8 -*-

from flask import jsonify, make_response
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Organization, ItemCollection, DiscountPolicy, DiscountCoupon, Price, CURRENCY_SYMBOL, LineItem
from utils import xhr_only


def jsonify_discount_policies(data_dict):
    discount_policies_list = []
    for policy in data_dict['discount_policies']:
        discount_policies_list.append({
            'id': policy.id,
            'title': policy.title,
            'discount_type': "Automatic" if policy.is_automatic else "Coupon based",
            'item_quantity_min': policy.item_quantity_min,
            'percentage': policy.percentage,
            'is_price_based': policy.is_price_based,
            'discount': Price.query.filter(Price.discount_policy == policy).first().amount if policy.is_price_based else policy.percentage,
            'currency': CURRENCY_SYMBOL['INR'],
            'dp_items': [{'id': str(item.id), 'title': item.title} for item in policy.items]
            })
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
    return jsonify(org_name=data_dict['org'].name, title=data_dict['org'].title, coupons=coupons_list)


@app.route('/admin/o/<org>/discount_policies')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_discount_policies}, json=True)
def admin_discount_policies(organization):
    discount_policies = DiscountPolicy.query.filter(DiscountPolicy.organization == organization).all()
    item_collection = ItemCollection.query.filter(ItemCollection.organization == organization).all()
    return dict(title=organization.title, org=organization, discount_policies=discount_policies, item_collection=item_collection)


@app.route('/admin/o/<org>/discount_policies/new', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@xhr_only
def admin_add_discount_policy(organization):
    return make_response(jsonify(status='ok', result={'message': 'New discount policy created'}), 201)


@app.route('/admin/<discount_policy_id>/edit', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_edit_discount_policy(discount_policy):
    return make_response(jsonify(status='ok', result={'message': 'Discount policy updated'}), 201)


@app.route('/admin/<discount_policy_id>/coupon', methods=['GET', 'OPTIONS', 'POST'])
@load_models(
    (DiscountPolicy, {'id': 'discount_policy_id'}, 'discount_policy'),
    permission='org_admin'
    )
@xhr_only
def admin_create_coupon(discount_policy):
    return make_response(jsonify(status='ok', result={'message': 'Discount coupon created'}), 201)


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
    (DiscountCoupon, {'id': 'coupon'}, 'coupon'),
    permission='org_admin'
    )
@xhr_only
def admin_discount_coupon(coupon):
    line_items = LineItem.query.filter(LineItem.discount_coupon == coupon).all()
    return make_response(jsonify(line_items=format_line_items(line_items)))
