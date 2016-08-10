
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {OrderView} from './admin_order.js';
import {DiscountPolicyView} from './admin_discount_policy.js';
import {DiscountCouponView} from './admin_coupon.js';

export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection",
    "ic/:icId/orders": "order",
    "o/:org/discount_policies": "discount_policy",
    "o/:org/coupons": "discount_coupon"
  },
  index: function() {
    IndexView.render();
  },
  org: function(org){
    OrgView.render({name: org});
  },
  item_collection: function(icId){
    ItemCollectionView.render({id: icId});
  },
  order: function(icId){
    OrderView.render({id: icId});
  },
  discount_policy: function(org){
    DiscountPolicyView.render({org_name: org});
  },
  discount_coupon: function(org){
    DiscountCouponView.render({org_name: org});
  }
});
