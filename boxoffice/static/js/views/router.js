
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {OrgReportView} from './admin_org_report.js';
import {DiscountPolicyView} from './admin_discount_policy.js';
import {ItemCollectionView} from './item_collection.js';
import {OrderView} from './admin_order.js';
import {ReportView} from './admin_report.js';

export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    "": "index",
    "o/:org_name": "org",
    "o/:org_name/reports": "org_report",
    "o/:org_name/discount_policy": 'discount_policy',
    "o/:org_name/discount_policy?:params": 'discount_policy',
    "ic/:ic_id": "item_collection",
    "ic/:ic_id/orders": "order",
    "ic/:ic_id/reports": "report"
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
  item_collection: function(ic_id) {
    ItemCollectionView.render({ic_id});
  },
  order: function(ic_id) {
    OrderView.render({ic_id});
  },
  report: function(ic_id) {
    ReportView.render({ic_id});
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
