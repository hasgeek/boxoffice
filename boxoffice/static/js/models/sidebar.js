import {OrgModel} from './org.js';
import {ItemCollectionModel} from './item_collection.js';
import {OrderModel} from './admin_order.js';

export const SideBarModel = {
  getItems: function(config) {
    let sidebar_items = [];
    if(config.org_name && config.ic_id) {
      sidebar_items = [
        {
          url: '/',
          title: 'Home',
          icon: 'fa-home',
          view: 'home'
        },
        {
          url: OrgModel.getUrl(config.org_name, true),
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: ItemCollectionModel.getUrl(config.ic_id, true),
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: OrderModel.getUrl(config.ic_id, true),
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        }
      ]
    }
    return sidebar_items;
  }
};
