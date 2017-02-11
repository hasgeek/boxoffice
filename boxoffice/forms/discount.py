# -*- coding: utf-8 -*-

from flask import g
from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectMultipleField
from coaster.utils import getbool
from ..models import DISCOUNT_TYPE, DiscountPolicy

__all__ = ['DiscountForm', 'DiscountCouponForm']


class DiscountForm(forms.Form):
    title = forms.StringField(__("Discount Title"), validators=[forms.validators.DataRequired((u"Please specify a discount title")), forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    is_price_based = forms.RadioField(__("Price based discount"), choices=[(True, 'Special price discount'), (False, 'Percentage based discount')], coerce=getbool, default=True)
    discount_type = forms.RadioField(__("Discount Type"), choices=DISCOUNT_TYPE.items(), coerce=int, default=1)
    percentage = forms.IntegerField(__("Percentage"), validators=[forms.validators.OptionalIf('is_price_based', (u"Please specify a discount percentage"))])
    item_quantity_min = forms.IntegerField(__("Minimum number of tickets"), default=1)
    discount_code_base = forms.StringField(__("Discount Title"), validators=[forms.validators.OptionalIfNot('discount_type', (u"Please specify a discount code base")), forms.validators.Length(max=20), forms.validators.StripWhitespace()])
    bulk_coupon_usage_limit = forms.IntegerField(__("Number of times a bulk coupon can be used"), default=1)
    price_title = forms.StringField(__("Price Title"), validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify a price title")), forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    amount = forms.IntegerField(__("Amount"), validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify the discounted price"))])
    start_at = forms.DateTimeField(__("Price start date"), format='%d %m %Y %H:%M:%S', timezone=lambda: g.user.timezone if g.user else None, validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify start date for the price"))])
    end_at = forms.DateTimeField(__("Price end date"), format='%d %m %Y %H:%M:%S', timezone=lambda: g.user.timezone if g.user else None, validators=[forms.validators.OptionalIfNot('is_price_based', (u"Please specify end date for the price"))])
    items = QuerySelectMultipleField(__("Items"), get_label='title', query_factory=lambda: [], validators=[forms.validators.DataRequired((u"Please select a item to which discount is to be applied"))])
    id = forms.StringField(__("id"), validators=[forms.validators.Optional()])

    def validate_discount_code_base(self, field):
        discount_policy = DiscountPolicy.query.filter_by(discount_code_base=field.data).first()
        if discount_policy and discount_policy != DiscountPolicy.query.filter_by(id=self.id.data).first():
            raise forms.ValidationError((u"Please specify a different discount code base"))

    def validate_end_at(self, field):
        if field.data <= self.start_at.data:
            raise forms.ValidationError((u"Please specify the price end date greater than start date"))


class DiscountCouponForm(forms.Form):
    count = forms.IntegerField(__("Number of coupons to be generated"), default=1)
    usage_limit = forms.IntegerField(__("Number of times each coupons can be used"), default=1)
    coupon_code = forms.StringField(__("Code for discount coupon"), validators=[forms.validators.Optional(), forms.validators.Length(max=100), forms.validators.StripWhitespace()], default='')
