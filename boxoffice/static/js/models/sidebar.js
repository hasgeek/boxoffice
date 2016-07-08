export const SideBarModel = {
  items: function(org, ic) {
    var sidebarItems = [
      {
        url: '/',
        title: 'Home',
        icon: 'fa-home'
      }
    ];
    if(org) {
      sidebarItems.push({
        url: '/o/' + org,
        title: 'Organization',
        icon: 'fa-sitemap'
      });
    }
    if(ic) {
      var icUrl = '/ic/' + ic;
      var itemcollectionSidebar = [
        {
          url: icUrl,
          title: 'Dashboard',
          icon: 'fa-dashboard'
        }
      ]
      sidebarItems = sidebarItems.concat(itemcollectionSidebar);
    }
    return sidebarItems;
  }
};
