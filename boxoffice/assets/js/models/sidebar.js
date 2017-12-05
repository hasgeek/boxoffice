import {urlFor} from './util.js';

export const SideBarModel = {
  getItems: function({org_name, org_title, ic_id, ic_title}={}) {
    let sidebar_items = [];
    if (org_name) {
      sidebar_items = [
        {
          url: '/',
          title: 'Home',
          icon: 'fa-home',
          view: 'home'
        },
        {
          url: urlFor('view', {resource: 'o', id: org_name}),
          title: org_title,
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: urlFor('index', {scope_ns: 'o', scope_id: org_name, resource: 'discount_policy'}),
          title: 'Discount Policies',
          icon: 'fa-tags',
          view: 'discount-policies',
          subItem: true
        },
        {
          url: urlFor('index', {resource: 'reports', scope_ns: 'o', scope_id: org_name}),
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'org_reports',
          subItem: true
        },
        {
          url: ic_id ? urlFor('view', {resource: 'ic', id: ic_id}) : "",
          title: ic_title,
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: ic_id ? urlFor('index', {resource: 'orders', scope_ns: 'ic', scope_id: ic_id}) : "",
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders',
          subItem: true
        },
        {
          url: ic_id ? urlFor('index', {resource: 'reports', scope_ns: 'ic', scope_id: ic_id}) : "",
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports',
          subItem: true
        }
      ]
    }
    return sidebar_items;
  }
};
