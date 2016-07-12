
import {OrdersModel} from '../models/admin_orders.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';

export const OrderView = {
  render: function(config) {
    let url = `/admin/ic/${config.id}/${config.orderId}`;
    OrdersModel.fetch({
      url: url
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data:  {
          title: remoteData.title,
          order: remoteData.order
        }
      });

      SideBarView.render('', {'org_name': remoteData.org_name, 'ic_id': config.id});

      NProgress.done();

      $('#order-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1400
        }
      });

      main_ractive.on('cancelTicket', function(event, method) {
        if(window.confirm("Are you sure you want to cancel this ticket?")) {
          main_ractive.set(event.keypath + '.cancel_error', "");
          main_ractive.set(event.keypath + '.cancelling', true);

          OrdersModel.post({
            url: event.context.cancel_ticket_url
          }).done(function(response) {
            main_ractive.set(event.keypath + '.cancelled_at', response.cancelled_at);
            main_ractive.set(event.keypath + '.cancelling', false);
          }).fail(function(response) {
            let error_text;
            if(response.readyState === 4) {
              if(response.status === 500) {
                error_text = "Server Error";
              }
              else {
                error_text = JSON.parse(response.responseText).message;
              }
            }
            else {
              error_text = "Unable to connect. Please try again later.";
            }
            main_ractive.set(event.keypath + '.cancel_error', error_text);
            main_ractive.set(event.keypath + '.cancelling', false);
          });
        }
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
