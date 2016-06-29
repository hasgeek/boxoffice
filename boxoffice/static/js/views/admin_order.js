
import {OrderModel} from '../models/admin_order.js';
// import {SideBarModel} from '../models/sidebar.js'
import {OrderTemplate} from '../templates/admin_order.html.js';
// import {SideBarComponent} from './sidebar.js'

export const OrderView = {
  render: function(config) {
    let url = `/admin/ic/${config.id}/${config.orderId}`;
    OrderModel.fetch({
      url: url
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data: remoteData
      });

      $('#order-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200
        }
      });

      // Setup polling
      let intervalId = setInterval(() => {
        OrderModel.fetch({
          url: url
        }).done((freshData) => {
          main_ractive.set(freshData);
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
