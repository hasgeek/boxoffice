
import {OrderModel} from '../models/admin_order.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';

export const OrderView = {
  render: function(config) {

    OrderModel.fetch({
      url: OrderModel.urlFor('index', {ic_id: config.id})['path']
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data:  {
          title: remoteData.title,
          orders: remoteData.orders
        }
      });

      SideBarView.render('orders', {'org_name': remoteData.org_name, 'ic_id': config.id});

      NProgress.done();

      $('#orders-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200,
          largescreen: 1900
        }
      });

      $('#orders-table').bind('footable_filtering', function (e) {
        let selected = $('#filter-status').find(':selected').val();
        if (selected && selected.length > 0) {
          e.filter += (e.filter && e.filter.length > 0) ? ' ' + selected : selected;
          e.clear = !e.filter;
        }
      });

      $('#filter-status').change(function (e) {
        e.preventDefault();
        $('#orders-table').trigger('footable_filter', {filter: $('#filter').val()});
      });

      main_ractive.on('showOrder', function(event){
        //Show individual order
        let order_id = event.context.id;
        OrderModel.fetch({
          url: OrderModel.urlFor('view_order', {order_id: order_id})['path']
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.line_items', remoteData.line_items);
          main_ractive.set(event.keypath + '.show_order', true);
        });
      });

      main_ractive.on('hideOrder', function(event){
        //Show individual order
        main_ractive.set(event.keypath + '.show_order', false);
      });

      main_ractive.on('cancelTicket', function(event, method) {
        if (window.confirm("Are you sure you want to cancel this ticket?")) {
          main_ractive.set(event.keypath + '.cancel_error', "");
          main_ractive.set(event.keypath + '.cancelling', true);

          OrderModel.post({
            url: event.context.cancel_ticket_url
          }).done(function(response) {
            main_ractive.set(event.keypath + '.cancelled_at', response.result.cancelled_at);
            main_ractive.set(event.keypath + '.cancelling', false);
          }).fail(function(response) {
            let error_text;
            if (response.readyState === 4) {
              if (response.status === 500) {
                error_text = "Server Error";
              }
              else {
                error_text = JSON.parse(response.responseText).error_description;
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
