
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

      main_ractive.on('cancelTicket', function(event, method){
        console.log("cancelTicket", event.context.cancel_ticket);
        clearInterval(intervalId);
        main_ractive.set(event.keypath + '.cancel_error', "");
        OrderModel.post({
          url: event.context.cancel_ticket
        }).done(function(response) {
          main_ractive.set(event.keypath + '.is_cancelled', true);
        }).fail(function(response) {
          let resp = JSON.parse(response.responseText);
          main_ractive.set(event.keypath + '.cancel_error', resp.message);
        });
      });

      window.addEventListener('popstate', (event) => {
        // kill interval
        clearInterval(intervalId);
      });
    });
  }
}
