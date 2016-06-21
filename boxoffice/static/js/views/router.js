
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {ItemView} from './item.js';

export const Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "item_collection",
    "item/:item_id": "item"
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
  item: function(item_id){
    ItemView.render({id: item_id});
  }
});
