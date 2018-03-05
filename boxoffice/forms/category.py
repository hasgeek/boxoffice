# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms

__all__ = ['CategoryForm']


class CategoryForm(forms.Form):
    title = forms.StringField(__("Category title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
        forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    seq = forms.IntegerField(__("Sequence"),
        description=__("The sequence of the category on the listing"),
        validators=[forms.validators.DataRequired(__("Please specify the sequence order"))])
