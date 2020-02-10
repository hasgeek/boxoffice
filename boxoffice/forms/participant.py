# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms

from ..models import Assignee, LineItem, Order, ORDER_STATUS

__all__ = ['AssigneeForm']


class AssigneeForm(forms.Form):
    email = forms.EmailField(
        __("Email"),
        validators=[forms.validators.DataRequired(), forms.validators.Length(max=254)],
    )
    fullname = forms.StringField(
        __("Full Name"), validators=[forms.validators.DataRequired()]
    )
    phone = forms.StringField(
        __("Phone number"), validators=[forms.validators.DataRequired()]
    )

    def validate_email(self, field):
        existing_assignees = (
            self.edit_parent.assignees.filter(LineItem.order == self.edit_parent.order)
            .filter(Order.status != ORDER_STATUS.CANCELLED)
            .filter(Assignee.current == True)
            .filter(Assignee.email == field.data)
        )
        if self.edit_obj is not None:
            existing_assignees = existing_assignees.filter(
                Assignee.id != self.edit_obj.id
            )
        if existing_assignees.count() > 0:
            raise forms.ValidationError(__("Email address has been already used"))
