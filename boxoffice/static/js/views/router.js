
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';

export const Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection",
    "ic/:icId/orders": "orders"
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
    console.log("orders");
  }
});
