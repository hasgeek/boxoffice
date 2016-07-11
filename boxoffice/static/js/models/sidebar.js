export const SideBarModel = {
  getItems: function(config) {
    var sidebar_items = [];
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
        }
      ]
    }
    return sidebar_items;
  }
};
