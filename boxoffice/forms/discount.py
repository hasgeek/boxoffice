# -*- coding: utf-8 -*-

from baseframe import _
import baseframe.forms as forms
from baseframe.forms.sqlalchemy import QuerySelectMultipleField, QuerySelectField
from coaster.utils import getbool
from ..models import DISCOUNT_TYPE, CURRENCY, Item, ItemCollection, db

__all__ = ['DiscountPolicyForm', 'DiscountPriceForm', 'DiscountCouponForm', 'AutomaticDiscountPolicyForm', 'CouponBasedDiscountPolicyForm']


class DiscountPolicyForm(forms.Form):
    title = forms.StringField(_("Discount title"),
        validators=[forms.validators.DataRequired(_("Please specify a discount title")),
        forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    discount_type = forms.RadioField(_("Discount Type"),
        choices=DISCOUNT_TYPE.items(), coerce=int, default=DISCOUNT_TYPE.keys()[1])
    is_price_based = forms.RadioField(_("Price based discount"),
        choices=[(True, _("Special price discount")),
        (False, _("Percentage based discount"))], coerce=getbool, default=True)


class AutomaticDiscountPolicyForm(DiscountPolicyForm):
    item_quantity_min = forms.IntegerField(_("Minimum number of tickets"), default=1)
    percentage = forms.IntegerField(_("Percentage"),
        validators=[forms.validators.DataRequired(_("Please specify a discount percentage"))])
    items = QuerySelectMultipleField(_("Items"), get_label='title',
        validators=[forms.validators.DataRequired(_("Please select a item to which discount is to be applied"))])

    def __init__(self, *args, **kwargs):
        super(AutomaticDiscountPolicyForm, self).__init__(*args, **kwargs)
        self.items.query = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == self.edit_parent).options(db.load_only('id', 'title'))


class CouponBasedDiscountPolicyForm(DiscountPolicyForm):
    items = QuerySelectMultipleField(_("Items"), get_label='title',
        validators=[forms.validators.DataRequired(_("Please select a item to which discount is to be applied"))])
    percentage = forms.IntegerField(_("Percentage"),
        validators=[forms.validators.DataRequired(_("Please specify a discount percentage"))])
    discount_code_base = forms.NullTextField(_("Discount Title"),
        validators=[forms.validators.DataRequired(_("Please specify a discount code base")),
        forms.validators.Length(max=20), forms.validators.StripWhitespace()])
    bulk_coupon_usage_limit = forms.IntegerField(_("Number of times a bulk coupon can be used"), default=1)

    def __init__(self, *args, **kwargs):
        super(CouponBasedDiscountPolicyForm, self).__init__(*args, **kwargs)
        self.items.query = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == self.edit_parent).options(db.load_only('id', 'title'))


class DiscountPriceForm(forms.Form):
    title = forms.StringField(_("Discount price title"),
        validators=[forms.validators.DataRequired(_("Please specify a title for the discount price")),
        forms.validators.Length(max=250), forms.validators.StripWhitespace()])
    amount = forms.IntegerField(_("Amount"),
        validators=[forms.validators.DataRequired(_("Please specify an amount"))])
    currency = forms.RadioField(_("Currency"),
        validators=[forms.validators.DataRequired(_("Please select the currency"))],
        choices=CURRENCY.items(), default=CURRENCY.INR)
    start_at = forms.DateTimeField(_("Price start date"), format='%d %b %Y %H:%M:%S',
        validators=[forms.validators.DataRequired(_("Please specify a start date and time"))])
    end_at = forms.DateTimeField(_("Price end date"), format='%d %b %Y %H:%M:%S',
        validators=[forms.validators.DataRequired(_("Please specify an end date and time")),
        forms.validators.GreaterThan('start_at', _(u"Please specify the end date for the price that is greater than start date"))])
    item = QuerySelectField(_("Item"), get_label='title',
        validators=[forms.validators.DataRequired(_("Please select a item to which the discount is to be applied"))])

    def __init__(self, *args, **kwargs):
        super(DiscountPriceForm, self).__init__(*args, **kwargs)
        self.item.query = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == self.edit_parent.organization).options(db.load_only('id', 'title'))


class DiscountCouponForm(forms.Form):
    count = forms.IntegerField(_("Number of coupons to be generated"), default=1)
    usage_limit = forms.IntegerField(_("Number of times each coupon can be used"), default=1)
    coupon_code = forms.NullTextField(_("Code for discount coupon"),
            validators=[forms.validators.Optional(), forms.validators.Length(max=100),
            forms.validators.StripWhitespace()])
