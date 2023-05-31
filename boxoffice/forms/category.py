from __future__ import annotations

from typing import Optional

from baseframe import __, forms
from baseframe.forms.validators import StopValidation

from ..models import Category, db

__all__ = ['CategoryForm']


# TODO: Add to baseframe.forms.validators.AvailableAttr?
def available_seq(form: CategoryForm, field: forms.Field) -> None:
    basequery = db.session.query(Category.id).filter(
        Category.item_collection == form.edit_parent, Category.seq == field.data
    )
    if form.edit_obj:
        basequery = basequery.filter(Category.id != form.edit_obj.id)

    if basequery.scalar() is not None:
        raise StopValidation(
            __(
                "This sequence number has already been used. Please pick a different"
                " number"
            )
        )


class CategoryForm(forms.Form):
    edit_obj: Optional[Category]

    title = forms.StringField(
        __("Category title"),
        validators=[
            forms.validators.DataRequired(__("Please specify a title")),
            forms.validators.Length(max=250),
        ],
        filters=[forms.filters.strip()],
    )
    seq = forms.IntegerField(
        __("Sequence"),
        description=__("The sequence of the category on the listing"),
        validators=[
            forms.validators.DataRequired(__("Please specify the sequence order")),
            available_seq,
        ],
    )
