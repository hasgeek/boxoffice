# -*- coding: utf-8 -*-

from flask import jsonify, make_response
from .. import app, lastuser
from coaster.views import load_models, render_with
from boxoffice.models import Organization, DiscountPolicy, DiscountCoupon, Price, CURRENCY_SYMBOL, LineItem
from utils import xhr_only


def format_line_items(line_items):
    line_items_dict = []
    for line_item in line_items:
        line_items_dict.append({
            'item_title': line_item.item.title,
            'fullname': line_item.order.buyer_fullname,
            'email': line_item.order.buyer_email,
            'invoice_no': line_item.order.invoice_no
            })
    return line_items_dict


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


def jsonify_admin_coupons(data_dict):
    coupons_dicts = []
    discount_policies = DiscountPolicy.query.filter(DiscountPolicy.organization == data_dict['org']).all()
    for discount_policy in discount_policies:
        discount_coupons = DiscountCoupon.query.filter(DiscountCoupon.discount_policy == discount_policy).all()
        for coupon in discount_coupons:
            coupons_dicts.append(format_coupons(coupon))
    return jsonify(org_name=data_dict['org'].name, title=data_dict['org'].title, coupons=coupons_dicts)


@app.route('/admin/o/<org>/coupons')
@lastuser.requires_login
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@render_with({'text/html': 'index.html', 'application/json': jsonify_admin_coupons}, json=True)
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
