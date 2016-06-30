
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {OrdersView} from './admin_orders.js';
import {OrderView} from './admin_order.js';

export const Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection",
    "ic/:icId/orders": "orders",
    "ic/:icId/:orderId": "order",
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
  orders: function(icId){
    OrdersView.render({id: icId});
  },
  order: function(icId, orderId){
    OrderView.render({id: icId, orderId: orderId});
  }
});
