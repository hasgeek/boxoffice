# -*- coding: utf-8 -*-

from flask import g
from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectMultipleField, QuerySelectField
from coaster.utils import getbool
from ..models import DISCOUNT_TYPE, DiscountPolicy, CURRENCY

__all__ = ['DiscountPolicyForm', 'DiscountPriceForm', 'DiscountCouponForm']


class DiscountPolicyForm(forms.Form):
    title = forms.StringField(__("Discount Title"),
        validators=[forms.validators.DataRequired((u"Please specify a discount title")),
        forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    is_price_based = forms.RadioField(__("Price based discount"),
        choices=[(True, 'Special price discount'),
        (False, 'Percentage based discount')], coerce=getbool, default=True)
    discount_type = forms.RadioField(__("Discount Type"),
        choices=DISCOUNT_TYPE.items(), coerce=int, default=1)
    percentage = forms.IntegerField(__("Percentage"),
        validators=[forms.validators.OptionalIf('is_price_based', (u"Please specify a discount percentage"))])
    item_quantity_min = forms.IntegerField(__("Minimum number of tickets"), default=1)
    discount_code_base = forms.StringField(__("Discount Title"),
        validators=[forms.validators.OptionalIfNot('discount_type',
            (u"Please specify a discount code base")),
        forms.validators.Length(max=20), forms.validators.StripWhitespace()], filters=[lambda code_base: code_base or None])
    bulk_coupon_usage_limit = forms.IntegerField(__("Number of times a bulk coupon can be used"), default=1)
    items = QuerySelectMultipleField(__("Items"), get_label='title', query_factory=lambda: [],
        validators=[forms.validators.OptionalIf('is_price_based', (u"Please select a item to which discount is to be applied"))])
    # For validate_discount_code_base
    discount_policy_id = forms.StringField(__("Id"),
        validators=[forms.validators.Optional()], default=None)

    def validate_discount_code_base(self, field):
        if self.discount_policy_id.data:
            if DiscountPolicy.query.filter(DiscountPolicy.id != self.discount_policy_id.data, DiscountPolicy.discount_code_base == field.data).notempty():
                raise forms.ValidationError((u"Please specify a different discount code base"))
        elif DiscountPolicy.query.filter_by(discount_code_base=field.data).notempty():
            raise forms.ValidationError((u"Please specify a different discount code base"))


class DiscountPriceForm(forms.Form):
    title = forms.StringField(__("Discount price title"),
        validators=[forms.validators.DataRequired((u"Please specify a title for the discount price")),
        forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    is_price_based = forms.RadioField(__("Price based discount"),
        choices=[(True, 'Special price discount'),
        (False, 'Percentage based discount')], coerce=getbool, default=True)
    amount = forms.IntegerField(__("Amount"),
        validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify an amount"))])
    currency = forms.RadioField(__("Currency"),
        validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please select the currency"))],
        choices=CURRENCY.items(), default='INR')
    start_at = forms.DateTimeField(__("Price start date"), format='%d %b %Y %H:%M:%S',
        timezone=lambda: g.user.timezone,
        validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify a start date and time"))])
    end_at = forms.DateTimeField(__("Price end date"), format='%d %b %Y %H:%M:%S',
        timezone=lambda: g.user.timezone,
        validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify an end date and time"))])
    item = QuerySelectField(__("Item"), get_label='title', query_factory=lambda: [],
        validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please select a item to which the discount is to be applied"))])

    def validate_end_at(self, field):
        if field.data <= self.start_at.data:
            raise forms.ValidationError((u"Please specify the end date for the price that is greater than start date"))


class DiscountCouponForm(forms.Form):
    count = forms.IntegerField(__("Number of coupons to be generated"), default=1)
    usage_limit = forms.IntegerField(__("Number of times each coupon can be used"), default=1)
    coupon_code = forms.StringField(__("Code for discount coupon"),
        validators=[forms.validators.Optional(),
        forms.validators.Length(max=100),
        forms.validators.StripWhitespace()], default='')
