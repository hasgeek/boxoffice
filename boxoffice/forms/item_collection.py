# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms

__all__ = ['ItemCollectionForm']


class ItemCollectionForm(forms.Form):
    title = forms.StringField(__("Item Collection title"),
        validators=[forms.validators.DataRequired(__("Please specify a title")),
        forms.validators.Length(max=250)], filters=[forms.filters.strip()])
    description = forms.TinyMce4Field(__("Description"))
    tax_type = forms.SelectField(__("Tax type"), choices=[('GST', 'GST')], default='GST')
