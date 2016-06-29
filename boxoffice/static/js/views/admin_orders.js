
import {OrdersModel} from '../models/admin_orders.js';
// import {SideBarModel} from '../models/sidebar.js'
import {OrdersTemplate} from '../templates/admin_orders.html.js';
// import {SideBarComponent} from './sidebar.js'

export const OrdersView = {
  render: function(config) {
    let url = `/admin/ic/${config.id}/orders`;
    OrdersModel.fetch({
      url: url
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: OrdersTemplate,
        data: remoteData
      });

      $('#orders-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200
        }
      });

      // Setup polling
      let intervalId = setInterval(() => {
        OrdersModel.fetch({
          url: url
        }).done((freshData) => {
          main_ractive.set(freshData);
          $('#orders-table').trigger('footable_redraw'); //force a redraw
        });
      }, 3000);

      main_ractive.on('navigate', function(event, method){
        // kill interval
        clearInterval(intervalId);
        eventBus.trigger('navigate', event.context.url);
      });

      window.addEventListener('popstate', (event) => {
        // kill interval
        clearInterval(intervalId);
      });
    });
  }
}
