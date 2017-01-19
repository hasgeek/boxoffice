import {IndexModel} from './index.js';
import {OrgModel} from './org.js';
import {ItemCollectionModel} from './item_collection.js';
import {OrderModel} from './admin_order.js';
import {ReportModel} from './admin_report.js';

export const SideBarModel = {
  getItems: function(config) {
    let sidebarItems = [];
    if (config.orgName && config.icId) {
      sidebarItems = [
        {
          url: IndexModel.urlFor('index')['relativePath'],
          title: 'Home',
          icon: 'fa-home',
          view: 'home'
        },
        {
          url: OrgModel.urlFor('index', {orgName: config.orgName})['relativePath'],
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: ItemCollectionModel.urlFor('index', {icId: config.icId})['relativePath'],
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: OrderModel.urlFor('index', {icId: config.icId})['relativePath'],
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        },
        {
          url: ReportModel.urlFor('index', {icId: config.icId})['relativePath'],
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports'
        }
      ]
    }
    return sidebarItems;
  }
};
