# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from coaster.utils import getbool

__all__ = ['DiscountForm']


class DiscountForm(forms.Form):
    title = forms.StringField(__("Discount Title"), validators=[forms.validators.DataRequired(__(u"Please specify a discount title")), forms.validators.StripWhitespace()])
    is_price_based = forms.RadioField(__("Price based discount"), coerce=getbool, validators=[forms.validators.InputRequired(__(u"Please specify if it is a price based discount"))])
    discount_type = forms.RadioField(__("Discount Type"), coerce=getbool, validators=[forms.validators.OptionalIfNot(is_price_based)])
    item_quantity_min = forms.IntegerField(__("Minimum number of tickets"), validators=[forms.validators.DataRequired()])
    items = forms.SelectField(__("Discounted Item"), validators=[forms.validators.OptionalIf(is_price_based)])
    price_title = forms.StringField(__("Price Title"), validators=[forms.validators.OptionalIf(is_price_based), forms.validators.StripWhitespace()])
    amount = forms.IntegerField(__("Amount"), validators=[forms.validators.OptionalIf(is_price_based)])
    start_at = forms.DateTimeField(__("Price start date"), validators=[forms.validators.OptionalIf(is_price_based)])
    end_at = forms.DateTimeField(__("Price end date"), validators=[forms.validators.OptionalIf(is_price_based)])
    items = forms.SelectMultipleField(__("Discounted Items"), validators=[forms.validators.OptionalIfNot(is_price_based)])
    percentage = forms.IntegerField(__("Percentage"), validators=[forms.validators.OptionalIfNot(is_price_based)])
    organization = forms.StringField(__("Organization"), validators=[forms.validators.DataRequired(__(u"Please specify the organization"))])
