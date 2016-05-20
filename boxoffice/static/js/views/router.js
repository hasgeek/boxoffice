
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './org.js';

export const Router = Backbone.Router.extend({
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:ic": "item_collection"
  },
  index: function() {
    IndexView.render();
  },
  org: function(org){
    OrgView.render({name: org});
  },
  item_collection: function(ic){
    ItemCollectionView.render({name: ic});
  }
});
