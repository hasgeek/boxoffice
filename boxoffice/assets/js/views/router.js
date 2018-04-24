var Backbone = require("backbone");
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {OrgReportView} from './admin_org_report.js';
import {DiscountPolicyView} from './admin_discount_policy.js';
import {DeleteDiscountPolicyView} from './delete_discount_policy.js';
import {ItemCollectionView} from './item_collection.js';
import {ItemCollectionNewView} from './new_item_collection.js';
import {ItemCollectionEditView} from './edit_item_collection.js';
import {OrdersView} from './admin_orders.js';
import {OrderView} from './admin_order.js';
import {ReportView} from './admin_report.js';
import {ItemView} from './admin_item.js';
import {NewItemView} from './new_item.js';
import {EditItemView} from './edit_item.js';
import {NewPriceView} from './new_price.js';
import {EditPriceView} from './edit_price.js';
import {NewCategoryView} from './new_category.js';
import {EditCategoryView} from './edit_category.js';
import {PartialRefundOrderView} from './partial_refund_order.js';


export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    "": "index",
    "o/:org_name": "org",
    "o/:org_name/reports": "org_report",
    "o/:org_name/discount_policy": 'discount_policy',
    "o/:org_name/discount_policy/:id/delete": 'delete_discount_policy',
    "o/:org_name/discount_policy?:params": 'discount_policy',
    "ic/:ic_id": "item_collection",
    "ic/:ic_id/reports": "report",
    "o/:org_name/ic/new": "new_item_collection",
    "ic/:ic_id/edit": "edit_item_collection",
    "ic/:ic_id/orders": "orders",
    "o/:org_name/order/:order_receipt_no": "order",
    "ic/:ic_id/item/new": "new_item",
    "item/:item_id/edit": "edit_item",
    "item/:item_id": "item",
    "item/:item_id/price/new": "new_price",
    "item/:item_id/price/:price_id/edit": "edit_price",
    "ic/:ic_id/category/new": "new_category",
    "ic/:ic_id/category/:category_id/edit": "edit_category",
    "ic/:ic_id/order/:order_id/partial_refund": "partial_refund_order"
  },
  index: function() {
    IndexView.render();
  },
  org: function(org_name) {
    OrgView.render({org_name});
  },
  org_report: function(org_name) {
    OrgReportView.render({org_name});
  },
  discount_policy: function(org_name, {search, page, size}={}) {
    DiscountPolicyView.render({org_name, search, page, size});
  },
  delete_discount_policy: function(org_name, id) {
    DeleteDiscountPolicyView.render({org_name, id});
  },
  item_collection: function(ic_id) {
    ItemCollectionView.render({ic_id});
  },
  new_item_collection: function(org_name){
    if (window.boxofficeFirstLoad){
      OrgView.render({org_name});
    }
    ItemCollectionNewView.render({org_name});
  },
  edit_item_collection: function(ic_id){
    if (window.boxofficeFirstLoad){
      ItemCollectionView.render({ic_id});
    }
    ItemCollectionEditView.render({ic_id});
  },
  new_item: function(ic_id){
    if (window.boxofficeFirstLoad){
      ItemCollectionView.render({ic_id});
    }
    NewItemView.render({ic_id});
  },
  edit_item: function(item_id){
    if (window.boxofficeFirstLoad){
      ItemView.render({item_id});
    }
    EditItemView.render({item_id});
  },
  new_price: function(item_id){
    if (window.boxofficeFirstLoad){
      ItemView.render({item_id});
    }
    NewPriceView.render({item_id});
  },
  edit_price: function(item_id, price_id){
    if (window.boxofficeFirstLoad){
      ItemView.render({item_id});
    }
    EditPriceView.render({item_id, price_id});
  },
  new_category: function(ic_id){
    if (window.boxofficeFirstLoad){
      ItemCollectionView.render({ic_id});
    }
    NewCategoryView.render({ic_id});
  },
  edit_category: function(ic_id, category_id){
    if (window.boxofficeFirstLoad){
      ItemCollectionView.render({ic_id});
    }
    EditCategoryView.render({ic_id, category_id});
  },
  orders: function(ic_id) {
    OrdersView.render({ic_id});
  },
  order: function(org_name, order_receipt_no) {
    OrderView.render({org_name, order_receipt_no});
  },
  report: function(ic_id) {
    ReportView.render({ic_id});
  },
  item: function(item_id) {
    ItemView.render({item_id});
  },
  partial_refund_order: function(ic_id, order_id){
    if (window.boxofficeFirstLoad){
      ItemCollectionView.render({ic_id});
    }
    PartialRefundOrderView.render({ic_id, order_id});
  },
  _extractParameters: function(route, fragment) {
    var result = route.exec(fragment).slice(1);
    if (result[result.length-1]) {
      var paramString = result[result.length-1].split('&');
      var params = {};
      paramString.forEach(function(value){
        if(value){
          var param = value.split('=');
          params[param[0]] = param[1];
        }
      });
      result[result.length-1] = params;
    }
    return result;
  }
});
