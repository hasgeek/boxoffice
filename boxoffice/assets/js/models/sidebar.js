import { urlFor } from './util';

export const SideBarModel = {
  getItems({ accountName, accountTitle, menuId, menuTitle } = {}) {
    let sidebarItems = [];
    if (accountName) {
      sidebarItems = [
        {
          url: '/',
          title: 'Home',
          icon: 'fa-home',
          view: 'home',
        },
        {
          url: urlFor('view', { resource: 'o', id: accountName }),
          title: accountTitle,
          icon: 'fa-sitemap',
          view: 'org',
        },
        {
          url: urlFor('index', {
            scope_ns: 'o',
            scope_id: accountName,
            resource: 'discount_policy',
          }),
          title: 'Discount Policies',
          icon: 'fa-tags',
          view: 'discount-policies',
          subItem: true,
        },
        {
          url: urlFor('index', {
            resource: 'reports',
            scope_ns: 'o',
            scope_id: accountName,
          }),
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'org_reports',
          subItem: true,
        },
        {
          url: menuId ? urlFor('view', { resource: 'menu', id: menuId }) : '',
          title: menuTitle,
          icon: 'fa-dashboard',
          view: 'dashboard',
        },
        {
          url: menuId
            ? urlFor('index', {
                resource: 'orders',
                scope_ns: 'menu',
                scope_id: menuId,
              })
            : '',
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders',
          subItem: true,
        },
        {
          url: menuId
            ? urlFor('index', {
                resource: 'reports',
                scope_ns: 'menu',
                scope_id: menuId,
              })
            : '',
          title: 'Reports',
          icon: 'fa-file-excel-o',
          view: 'reports',
          subItem: true,
        },
      ];
    }
    return sidebarItems;
  },
};

export { SideBarModel as default };
