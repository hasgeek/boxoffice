# -*- coding: utf-8 -*-

from flask_admin.contrib.sqla import ModelView
from . import lastuser
from flask_admin.form.fields import JSONField


class SiteAdminModelView(ModelView):
    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


class OrganizationModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_list = ('id', 'title', 'organization_id')
    form_list = ('id', 'userid', 'title')
    form_excluded_columns = ['userid', 'item_collections', 'discount_policies', 'invoices', 'orders', 'created_at', 'updated_at']
    form_overrides = dict(details=JSONField)


class DiscountCouponModelView(SiteAdminModelView):
    can_delete = False
    column_filters = ['discount_policy']
    column_searchable_list = ['code']
    column_list = ('code', 'discount_policy')
    form_excluded_columns = ['line_items', 'created_at', 'updated_at']


class InvoiceModelView(SiteAdminModelView):
    can_delete = False
    column_filters = ['invoice_no']
    column_searchable_list = ['invoicee_email']
    column_list = ('customer_order_id', 'invoice_no', 'invoicee_name', 'invoicee_email')
    form_excluded_columns = ['customer_order_id', 'organization_id', 'created_at', 'updated_at']
