import {IndexModel} from './index.js';
import {OrgModel} from './org.js';
import {ItemCollectionModel} from './item_collection.js';
import {OrderModel} from './admin_order.js';
import {DiscountPolicyModel} from './admin_discount_policy.js';
import {ReportModel} from './admin_report.js';

export const SideBarModel = {
  getItems: function({org_name, ic_id}={}) {
    let sidebar_items = [];
    this.org_name = org_name ? org_name : this.org_name;
    this.ic_id = ic_id ? ic_id : this.ic_id;
    if (org_name) {
      sidebar_items = [
        {
          url: IndexModel.urlFor('index')['relative_path'],
          title: 'Home',
          icon: 'fa-home',
          view: 'home'
        },
        {
          url: OrgModel.urlFor('index', {org_name})['relative_path'],
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: this.ic_id ? ItemCollectionModel.urlFor('index', {ic_id: this.ic_id})['relative_path'] : "",
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: this.ic_id ? OrderModel.urlFor('index', {ic_id: this.ic_id})['relative_path'] : "",
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        },
        {
          url: DiscountPolicyModel.urlFor('index', {org_name})['relative_path'],
          title: 'Discount Policies',
          icon: 'fa-tags',
          view: 'discount-policies'
        },
        {
          url: this.ic_id ? ReportModel.urlFor('index', {ic_id: this.ic_id})['relative_path'] : "",
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports'
        }
      ]
    }
    return sidebar_items;
  }
};
