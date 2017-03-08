# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectMultipleField, QuerySelectField
from coaster.utils import getbool
from ..models import DISCOUNT_TYPE, DiscountPolicy, CURRENCY

__all__ = ['DiscountPolicyForm', 'DiscountPriceForm', 'DiscountCouponForm']


class DiscountPolicyForm(forms.Form):
    title = forms.StringField(__("Discount title"),
        validators=[forms.validators.DataRequired(__("Please specify a discount title")),
        forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    is_price_based = forms.RadioField(__("Price based discount"),
        choices=[(True, __("Special price discount")),
        (False, __("Percentage based discount"))], coerce=getbool, default=True)
    discount_type = forms.RadioField(__("Discount Type"),
        choices=DISCOUNT_TYPE.items(), coerce=int, default=DISCOUNT_TYPE.values()[1])
    percentage = forms.IntegerField(__("Percentage"),
        validators=[forms.validators.OptionalIf('is_price_based', __("Please specify a discount percentage"))])
    item_quantity_min = forms.IntegerField(__("Minimum number of tickets"), default=1)
    discount_code_base = forms.NullTextField(__("Discount Title"),
        validators=[forms.validators.OptionalIfNot('discount_type', __("Please specify a discount code base")),
        forms.validators.Length(max=20), forms.validators.StripWhitespace()])
    bulk_coupon_usage_limit = forms.IntegerField(__("Number of times a bulk coupon can be used"), default=1)
    items = QuerySelectMultipleField(__("Items"), get_label='title', query_factory=lambda: [],
        validators=[forms.validators.OptionalIf('is_price_based', __("Please select a item to which discount is to be applied"))])
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
        validators=[forms.validators.DataRequired(__("Please specify a title for the discount price")),
        forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    amount = forms.IntegerField(__("Amount"),
        validators=[forms.validators.DataRequired(__("Please specify an amount"))])
    currency = forms.RadioField(__("Currency"),
        validators=[forms.validators.DataRequired(__("Please select the currency"))],
        choices=CURRENCY.items(), default=CURRENCY.INR)
    start_at = forms.DateTimeField(__("Price start date"),
        validators=[forms.validators.DataRequired(__("Please specify a start date and time"))])
    end_at = forms.DateTimeField(__("Price end date"),
        validators=[forms.validators.DataRequired(__("Please specify an end date and time")),
        forms.validators.GreaterThan('start_at', __(u"Please specify the end date for the price that is greater than start date"))])
    item = QuerySelectField(__("Item"), get_label='title', query_factory=lambda: [],
        validators=[forms.validators.DataRequired(__("Please select a item to which the discount is to be applied"))])


class DiscountCouponForm(forms.Form):
    count = forms.IntegerField(__("Number of coupons to be generated"), default=1)
    usage_limit = forms.IntegerField(__("Number of times each coupon can be used"), default=1)
    coupon_code = forms.NullTextField(__("Code for discount coupon"),
            validators=[forms.validators.Optional(), forms.validators.Length(max=100),
            forms.validators.StripWhitespace()])
