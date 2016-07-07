export const SideBarModel = {
  items: function(id) {
    let baseUrl = 'ic/' + id;
    return [
      {
        url: baseUrl,
        title: 'Dashboard',
        icon: 'fa-dashboard',
        view: 'dashboard'
      }
    ]
  }
};
