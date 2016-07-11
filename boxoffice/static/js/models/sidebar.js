export const SideBarModel = {
  getItems: function(org, ic) {
    var sidebar_items = [
      {
        url: '/',
        title: 'Home',
        icon: 'fa-home'
      }
    ];
    if(org) {
      sidebar_items.push({
        url: '/o/' + org,
        title: 'Organization',
        icon: 'fa-sitemap'
      });
    }
    if(ic) {
      var icUrl = '/ic/' + ic;
      var itemcollection_sidebar = [
        {
          url: icUrl,
          title: 'Dashboard',
          icon: 'fa-dashboard'
        }
      ];
      sidebar_items = sidebar_items.concat(itemcollection_sidebar);
    }
    return sidebar_items;
  }
};
