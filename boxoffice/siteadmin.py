from flask_admin.contrib.sqla import ModelView
from . import lastuser


class SiteAdminModelView(ModelView):
    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


class OrganizationModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_list = ('id', 'title')
    form_list = ('id', 'userid', 'title')
    form_excluded_columns = ['userid', 'item_collections', 'discount_policies', 'orders', 'created_at', 'updated_at']


class ItemCollectionModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['organization']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'items', 'orders', 'categories', 'created_at', 'updated_at']


class CategoryModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item_collection']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'items', 'created_at', 'updated_at']


class ItemModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item_collection']
    column_searchable_list = ['title']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'line_items', 'created_at', 'updated_at']


class PriceModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item']
    column_list = ('id', 'item', 'title', 'start_at', 'end_at', 'currency', 'amount')
    form_excluded_columns = ['parent', 'created_at', 'updated_at']


class DiscountPolicyModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['organization']
    column_list = ('id', 'title')
    column_searchable_list = ['title']
    form_excluded_columns = ['parent', 'line_items', 'created_at', 'updated_at', 'discount_coupons']


class DiscountCouponModelView(SiteAdminModelView):
    can_delete = False
    column_filters = ['discount_policy']
    column_searchable_list = ['code']
    column_list = ('code', 'discount_policy')
    form_excluded_columns = ['line_items', 'created_at', 'updated_at']
