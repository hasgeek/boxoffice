# -*- coding: utf-8 -*-

from boxoffice.models import db, Organization
from baseframe.forms.sqlalchemy import QuerySelectField
import baseframe.forms as forms
from coaster.utils import buid
from baseframe import __
from .utils import validate_json, format_json

__all__ = ['OrgForm', 'NewOrgForm']


def get_default_details():
    return {
        u'access_token': buid(),
        u'address': u'',
        u'cin': u'',
        u'logo': u'',
        u'pan': u'',
        u'refund_policy': u'',
        u'support_email': u'',
        u'ticket_faq': u'',
        u'website': u''
    }


class OrgForm(forms.Form):
    contact_email = forms.EmailField(__("Contact email"),
        validators=[
            forms.validators.DataRequired(__("We need a valid email address")),
            forms.validators.Length(min=5, max=80, message=__("%%(max)d characters maximum")),
            forms.validators.ValidEmail(__("This does not appear to be a valid email address"))],
        filters=[forms.filters.strip()])
    details = forms.TextAreaField(__("Details"), filters=[format_json],
        validators=[validate_json], default=get_default_details)
    invoicer = QuerySelectField(__("Parent organization"), get_label='title',
        validators=[forms.validators.DataRequired(__("Please select a parent organization"))])

    def set_queries(self):
        self.invoicer.query = Organization.query.filter(
            Organization.invoicer == None).options(db.load_only('id', 'title'))


class NewOrgForm(OrgForm):
    organization = forms.RadioField(u"Organization", validators=[forms.validators.DataRequired("Select an organization")],
        description=u"Select the organization you’d like to setup Boxoffice for")