# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms

__all__ = ['PriceForm']


class PriceForm(forms.Form):
    start_at = forms.DateTimeField(__("Price start date & time"))
    end_at = forms.DateTimeField(__("Price end date & time"),
        validators=[forms.validators.GreaterThan('start_at', __(u"The price can’t end before it starts"))])
    amount = forms.IntegerField(__("Amount"),
        validators=[forms.validators.DataRequired(__("Please specify an price amount"))])
    currency = forms.SelectField(__("Currency"), choices=[('INR', 'INR')], default='INR')
