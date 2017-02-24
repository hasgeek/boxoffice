import {urlFor} from './util.js';

export const SideBarModel = {
  getItems: function({org_name, ic_id}={}) {
    let sidebar_items = [];
    this.org_name = org_name ? org_name : this.org_name;
    this.ic_id = ic_id ? ic_id : this.ic_id;
    if (org_name) {
      sidebar_items = [
        {
          url: urlFor('home')['index']['relative_path'],
          title: 'Home',
          icon: 'fa-home',
          view: 'home'
        },
        {
          url: urlFor('org', {org_name})['index']['relative_path'],
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: this.ic_id ? urlFor('dashboard', {ic_id: this.ic_id})['index']['relative_path'] : "",
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: this.ic_id ? urlFor('orders', {ic_id: this.ic_id})['index']['relative_path'] : "",
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        },
        {
          url: urlFor('discount-policies', {org_name})['index']['relative_path'],
          title: 'Discount Policies',
          icon: 'fa-tags',
          view: 'discount-policies'
        },
        {
          url: this.ic_id ? urlFor('reports', {ic_id: this.ic_id})['index']['relative_path'] : "",
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports'
        }
      ]
    }
    return sidebar_items;
  }
};
