
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {OrderView} from './admin_order.js';
import {DiscountCouponView} from './admin_coupon.js';

export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection",
    "ic/:icId/orders": "order",
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
  discount_coupon: function(org){
    DiscountCouponView.render({org_name: org});
  }
});
