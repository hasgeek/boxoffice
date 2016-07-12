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
          url: '/o/' + config.org_name,
          title: 'Organization',
          icon: 'fa-sitemap',
          view: 'org'
        },
        {
          url: '/ic/' + config.ic_id,
          title: 'Dashboard',
          icon: 'fa-dashboard',
          view: 'dashboard'
        },
        {
          url: '/ic/' + config.ic_id + '/orders',
          title: 'Orders',
          icon: 'fa-shopping-cart',
          view: 'orders'
        }
      ]
    }
    return sidebar_items;
  }
};
