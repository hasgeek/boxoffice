from flask_admin.contrib.sqla import ModelView
from . import lastuser


class SiteAdminModelView(ModelView):

    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


class OrganizationModelView(SiteAdminModelView):
    column_display_pk = True
    column_list = ('id', 'title')
    form_list = ('id', 'userid', 'title')
    form_excluded_columns = ['userid', 'item_collections', 'discount_policies', 'orders', 'name', 'created_at', 'updated_at', 'name']


class ItemCollectionModelView(SiteAdminModelView):
    column_display_pk = True
    column_filters = ['organization']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'items', 'orders', 'categories', 'created_at', 'updated_at', 'name']


class ItemModelView(SiteAdminModelView):
    column_display_pk = True
    column_filters = ['item_collection']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'line_items', 'created_at', 'updated_at', 'name']


class PriceModelView(SiteAdminModelView):
    column_display_pk = True
    column_filters = ['item']
    column_list = ('id', 'item', 'title', 'start_at', 'end_at')
    form_excluded_columns = ['parent', 'created_at', 'updated_at', 'name']


class DiscountPolicyModelView(SiteAdminModelView):
    column_display_pk = True
    column_filters = ['organization']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'line_items', 'created_at', 'updated_at', 'name', 'discount_coupons']


class DiscountCouponModelView(SiteAdminModelView):
    column_filters = ['discount_policy']
    column_list = ('code', 'discount_policy')
    form_excluded_columns = ['line_items', 'created_at', 'updated_at']
