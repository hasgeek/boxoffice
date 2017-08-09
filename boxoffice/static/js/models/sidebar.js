import {urlFor} from './util.js';

export const SideBarModel = {
  getItems: function({org_name, ic_id}={}) {
    let sidebar_items = [];
    this.org_name = org_name ? org_name : this.org_name;
    this.ic_id = ic_id ? ic_id : this.ic_id;
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
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: urlFor('index', {resource: 'reports', scope_ns: 'o', scope_id: org_name}),
          title: 'Org reports',
          icon: 'fa-file-excel-o',
          view: 'org_reports'
        },
        {
          url: this.ic_id ? urlFor('view', {resource: 'ic', id: this.ic_id}) : "",
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: this.ic_id ? urlFor('index', {resource: 'orders', scope_ns: 'ic', scope_id: this.ic_id}) : "",
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        },
        {
          url: urlFor('index', {scope_ns: 'o', scope_id: org_name, resource: 'discount_policy'}),
          title: 'Discount Policies',
          icon: 'fa-tags',
          view: 'discount-policies'
        },
        {
          url: this.ic_id ? urlFor('index', {resource: 'reports', scope_ns: 'ic', scope_id: this.ic_id}) : "",
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports'
        }
      ]
    }
    return sidebar_items;
  }
};
