
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {OrderView} from './admin_order.js';
import {DiscountPolicyView} from './admin_discount_policy.js';

export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection",
    "ic/:icId/orders": "order",
    "o/:org/discount_policies": 'discount_policy',
    "o/:org/discount_policies?:params": 'discount_policy',
  },
  index: function() {
    IndexView.render();
  },
  org: function(org) {
    OrgView.render({name: org});
  },
  item_collection: function(icId) {
    ItemCollectionView.render({id: icId});
  },
  order: function(icId) {
    OrderView.render({id: icId});
  },
  discount_policy: function(org, params='') {
    if(params) {
      DiscountPolicyView.render({org_name: org, search: params.search, page: params.page});
    }
    else {
      DiscountPolicyView.render({org_name: org});
    }
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
