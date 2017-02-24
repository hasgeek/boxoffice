
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {OrderView} from './admin_order.js';
import {DiscountPolicyView} from './admin_discount_policy.js';
import {ReportView} from './admin_report.js';

export const Router = Backbone.Router.extend({
  url_root: '/api/1/admin/',
  routes: {
    "": "index",
    "o/:org_name": "org",
    "ic/:ic_id": "item_collection",
    "ic/:ic_id/orders": "order",
    ":org_name/discount_policy": 'discount_policy',
    ":org_name/discount_policy?:params": 'discount_policy',
    "ic/:ic_id/reports": "report"
  },
  index: function() {
    //View is 'home', used for urlFor().
    IndexView.render('home');
  },
  org: function(org_name) {
    OrgView.render('org', {org_name});
  },
  item_collection: function(ic_id) {
    ItemCollectionView.render('dashboard', {ic_id});
  },
  order: function(ic_id) {
    OrderView.render('orders', {ic_id});
  },
  discount_policy: function(org_name, {search, page}={}) {
    DiscountPolicyView.render('discount-policies', {org_name, search, page});
  },
  report: function(ic_id){
    ReportView.render('reports', {ic_id});
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
