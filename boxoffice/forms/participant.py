from __future__ import annotations

from baseframe import __, forms

from ..models import ORDER_STATUS, Assignee, Item, LineItem, Order

__all__ = ["AssigneeForm"]


class AssigneeForm(forms.Form):
    edit_obj: Assignee
    edit_parent: LineItem

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

    def validate_email(self, field: forms.Field) -> None:
        existing_assignees = (
            Assignee.query.join(LineItem)
            .join(Item)
            .join(Order)
            .filter(LineItem.item_id == self.edit_parent.item_id)
            .filter(Order.status != ORDER_STATUS.CANCELLED)
            .filter(Assignee.current.is_(True))
            .filter(Assignee.email == field.data)
        )
        if self.edit_obj is not None:
            existing_assignees = existing_assignees.filter(
                Assignee.id != self.edit_obj.id
            )
        if existing_assignees.count() > 0:
            raise forms.ValidationError(__("Email address has been already used"))
