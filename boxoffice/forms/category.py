# -*- coding: utf-8 -*-

from baseframe import __
import baseframe.forms as forms
from baseframe.forms.validators import StopValidation
from boxoffice.models import db, Category

__all__ = ['CategoryForm']


# TODO: Add to baseframe.forms.validators.AvailableAttr?
def available_seq(form, field):
	if db.session.query(Category.id).filter(
		Category.item_collection == form.edit_parent, Category.seq == field.data
		).scalar() is not None:
		raise StopValidation(__("This sequence number has already been used. Please pick a different number"))


class CategoryForm(forms.Form):
	title = forms.StringField(__("Category title"),
		validators=[forms.validators.DataRequired(__("Please specify a title")),
			forms.validators.Length(max=250)], filters=[forms.filters.strip()])
	seq = forms.IntegerField(__("Sequence"),
		description=__("The sequence of the category on the listing"),
		validators=[forms.validators.DataRequired(__("Please specify the sequence order")), available_seq])
