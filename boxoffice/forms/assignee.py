# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms

__all__ = ['AssigneeForm']


class AssigneeForm(forms.Form):
    email = forms.EmailField(__("Email"), validators=[forms.validators.DataRequired(), forms.validators.Length(max=80)])
    fullname = forms.StringField(__("Full name"), validators=[forms.validators.DataRequired()])
    phone = forms.StringField(__("Phone number"), validators=[forms.validators.Length(max=16)])
