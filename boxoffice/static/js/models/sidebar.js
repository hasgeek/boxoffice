export const SideBarModel = {
  items: function(id) {
    let baseUrl = 'ic/' + id;
    return [
      {
        url: baseUrl,
        title: 'DashBoard',
        icon: 'fa-dashboard',
        view: 'dashboard'
      }
    ]
  }
};
