
import {IndexView} from './index.js';
import {OrgView} from './org.js';
import {ItemCollectionView} from './item_collection.js';
import {OrderView} from './admin_order.js';
import {ReportView} from './admin_report.js';

export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    "": "index",
    "o/:org": "org",
    "ic/:icId": "itemCollection",
    "ic/:icId/orders": "order",
    "ic/:icId/reports": "report"
  },
  index: function() {
    IndexView.render();
  },
  org: function(org){
    OrgView.render({name: org});
  },
  itemCollection: function(icId){
    ItemCollectionView.render({id: icId});
  },
  order: function(icId){
    OrderView.render({id: icId});
  },
  report: function(icId){
    ReportView.render({id: icId});
  }
});
