# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectMultipleField, QuerySelectField
from coaster.utils import getbool
from baseframe.forms.validators import StopValidation
from baseframe.forms.sqlalchemy import AvailableAttr
from ..models import DISCOUNT_TYPE, CURRENCY, Item, ItemCollection, db, DiscountCoupon

__all__ = ['DiscountPolicyForm', 'PriceBasedDiscountPolicyForm', 'DiscountPriceForm', 'DiscountCouponForm', 'AutomaticDiscountPolicyForm', 'CouponBasedDiscountPolicyForm']


class DiscountPolicyForm(forms.Form):
    title = forms.StringField(__("Discount title"),
        validators=[forms.validators.DataRequired(__("Please specify a discount title")),
        forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    discount_type = forms.RadioField(__("Discount type"),
        choices=DISCOUNT_TYPE.items(), coerce=int, default=DISCOUNT_TYPE.COUPON)
    is_price_based = forms.RadioField(__("Price based discount"),
        coerce=getbool, default=1, choices=[
            (1, __("Special price discount")),
            (0, __("Percentage based discount"))])


def validate_percentage(form, field):
    if isinstance(field.data, int) and field.data < 0 or field.data > 100:
        raise StopValidation(__("Percentage should be a number from 0 to 100"))


class AutomaticDiscountPolicyForm(DiscountPolicyForm):
    item_quantity_min = forms.IntegerField(__("Minimum number of tickets"), default=1)
    percentage = forms.IntegerField(__("Percentage"),
        validators=[forms.validators.DataRequired(__("Please specify a discount percentage"))])
    items = QuerySelectMultipleField(__("Items"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select at least one item for which the discount is applicable"))])

    def set_queries(self):
        self.items.query = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == self.edit_parent).options(db.load_only('id', 'title'))


class CouponBasedDiscountPolicyForm(DiscountPolicyForm):
    items = QuerySelectMultipleField(__("Items"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select at least one item for which the discount is applicable"))])
    percentage = forms.IntegerField(__("Percentage"), validators=[validate_percentage])
    discount_code_base = forms.StringField(__("Discount title"),
        validators=[forms.validators.DataRequired(__("Please specify a discount code base")),
        forms.validators.Length(max=20), AvailableAttr('discount_code_base', message='This discount code base is already in use. Please pick a different code base.')],
        filters=[forms.filters.strip(), forms.filters.none_if_empty()])
    bulk_coupon_usage_limit = forms.IntegerField(__("Bulk coupon usage limit"), default=1)

    def set_queries(self):
        self.items.query = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == self.edit_parent).options(db.load_only('id', 'title'))


class PriceBasedDiscountPolicyForm(DiscountPolicyForm):
    discount_code_base = forms.StringField(__("Discount prefix"),
        validators=[forms.validators.DataRequired(__("Please specify a discount code base")),
            forms.validators.Length(max=20), AvailableAttr('discount_code_base', message='This discount code base is already in use. Please pick a different code base.')],
        filters=[forms.filters.strip(), forms.filters.none_if_empty()])


class DiscountPriceForm(forms.Form):
    title = forms.StringField(__("Discount price title"),
        validators=[forms.validators.DataRequired(__("Please specify a title for the discount price")),
        forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    amount = forms.IntegerField(__("Amount"),
        validators=[forms.validators.DataRequired(__("Please specify an amount"))])
    currency = forms.RadioField(__("Currency"),
        validators=[forms.validators.DataRequired(__("Please select the currency"))],
        choices=CURRENCY.items(), default=CURRENCY.INR)
    start_at = forms.DateTimeField(__("Price start date"),
        validators=[forms.validators.DataRequired(__("Please specify a start date and time"))])
    end_at = forms.DateTimeField(__("Price end date"),
        validators=[forms.validators.DataRequired(__("Please specify an end date and time")),
        forms.validators.GreaterThan('start_at', __("Please specify an end date for the price that is greater than the start date"))])
    item = QuerySelectField(__("Item"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select a item for which the discount is to be applied"))])

    def set_queries(self):
        self.item.query = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == self.edit_parent.organization).options(db.load_only('id', 'title'))


def validate_unique_discount_coupon_code(form, field):
    if DiscountCoupon.query.filter(DiscountCoupon.discount_policy == form.edit_parent, DiscountCoupon.code == field.data).notempty():
        raise StopValidation(__("This discount coupon code already exists. Please enter a different coupon code"))


class DiscountCouponForm(forms.Form):
    count = forms.IntegerField(__("Number of coupons to be generated"), default=1)
    usage_limit = forms.IntegerField(__("Number of times each coupon can be used"), default=1)
    code = forms.StringField(__("Discount coupon code"),
        validators=[forms.validators.Optional(), forms.validators.Length(max=100),
        validate_unique_discount_coupon_code],
        filters=[forms.filters.strip(), forms.filters.none_if_empty()])
