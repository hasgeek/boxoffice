
export const SideBarModel = Backbone.Model.extend({
  sideBarItems: function() {
    var baseUrl = 'ic/' + this.get('id');
    return [
      {
        url: baseUrl,
        title: 'DashBoard',
        icon: 'fa-dashboard',
        view: 'dashboard'
      },
      {
        url: baseUrl + '/items',
        title: 'Items',
        icon: 'fa-ticket',
        view: 'items'
      },
      {
        url: baseUrl + '/discounts',
        title: 'Discounts',
        icon: 'fa-tag',
        view: 'discounts'
      },
      {
        url: baseUrl + '/orders',
        title: 'Orders',
        icon: 'fa-shopping-cart',
        view: 'orders'
      },
      {
        url: baseUrl + '/assignees',
        title: 'Assignees',
        icon: 'fa-users',
        view: 'assignees'
      },
      {
        url: baseUrl + '/reports',
        title: 'Reports',
        icon: 'fa-area-chart',
        view: 'report'      
      }
    ]
  }
});
