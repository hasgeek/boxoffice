import {IndexModel} from './index.js';
import {OrgModel} from './org.js';
import {ItemCollectionModel} from './item_collection.js';
import {OrderModel} from './admin_order.js';
import {ReportModel} from './admin_report.js';

export const SideBarModel = {
  getItems: function(config) {
    let sidebar_items = [];
    if (config.org_name && config.ic_id) {
      sidebar_items = [
        {
          url: IndexModel.urlFor('index')['relative_path'],
          title: 'Home',
          icon: 'fa-home',
          view: 'home'
        },
        {
          url: OrgModel.urlFor('index', {org_name: config.org_name})['relative_path'],
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: ItemCollectionModel.urlFor('index', {ic_id: config.ic_id})['relative_path'],
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: OrderModel.urlFor('index', {ic_id: config.ic_id})['relative_path'],
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        },
        {
          url: ReportModel.urlFor('index', {ic_id: config.ic_id})['relative_path'],
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports'
        }
      ]
    }
    return sidebar_items;
  }
};
