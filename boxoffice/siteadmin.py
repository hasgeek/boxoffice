from flask_admin.contrib.sqla import ModelView
from . import lastuser


class SiteAdminModelView(ModelView):

    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


class ItemModelView(SiteAdminModelView):
    column_display_pk = True
    column_exclude_list = ['']
    column_filters = ['item_collection']
    column_list = ('id', 'title')
    form_excluded_columns = ['line_items', 'created_at', 'updated_at']


class PriceModelView(SiteAdminModelView):
    column_display_pk = True
    column_exclude_list = ['']
    column_list = ('id', 'item', 'title', 'start_at', 'end_at')
    form_excluded_columns = ['created_at', 'updated_at']


class DiscountPolicyModelView(SiteAdminModelView):
    column_display_pk = True
    column_exclude_list = ['']
    column_list = ('id', 'title')
    form_excluded_columns = ['line_items', 'created_at', 'updated_at', 'name', 'discount_coupons']


class DiscountCouponModelView(SiteAdminModelView):
    column_exclude_list = ['']
    column_list = ('code', 'discount_policy')
    form_excluded_columns = ['line_items', 'created_at', 'updated_at']
