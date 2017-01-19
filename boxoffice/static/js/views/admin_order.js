
import {Util, ScrollToElement} from '../models/util.js';
import {OrderModel} from '../models/admin_order.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';

export const OrderView = {
  render: function(config) {

    OrderModel.fetch({
      url: OrderModel.urlFor('index', {icId: config.id})['path']
    }).done((remoteData) => {
      // Initial render
      let orderComponent = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data:  {
          title: remoteData.title,
          orders: remoteData.orders,
          formatCurrency: function(value) {
            return Util.formatToIndianRupee(value);
          }
        }
      });

      SideBarView.render('orders', {'orgName': remoteData.org_name, 'icId': config.id});

      NProgress.done();

      $('#orders-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200,
          largescreen: 1900
        }
      });

      $('#orders-table').on('footable_filtering', function (e) {
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

      $("#search-form").on("keypress", function(e) {
        if (e.which == 13) {
          return false;
        }
      });

      orderComponent.on('showOrder', function(event){
        //Close all other open side panels
        orderComponent.set('orders.*.showOrder', false);
        //Show individual order
        orderComponent.set(event.keypath + '.loading', true);
        NProgress.configure({ showSpinner: false}).start();
        let orderId = event.context.id;
        OrderModel.fetch({
          url: OrderModel.urlFor('view', {orderId: orderId})['path']
        }).done((remoteData) => {
          orderComponent.set(event.keypath + '.lineItems', remoteData.line_items);
          orderComponent.set(event.keypath + '.showOrder', true);
          NProgress.done();
          orderComponent.set(event.keypath + '.loading', false);
          let ractiveId = "#" + orderComponent.el.id;
          //Scroll to the top of the page to view the order slider
          ScrollToElement(ractiveId);
        });
      });

      orderComponent.on('hideOrder', function(event){
        //Show individual order
        orderComponent.set(event.keypath + '.showOrder', false);
      });

      orderComponent.on('cancelTicket', function(event, method) {
        if (window.confirm("Are you sure you want to cancel this ticket?")) {
          orderComponent.set(event.keypath + '.cancelError', "");
          orderComponent.set(event.keypath + '.cancelling', true);

          OrderModel.post({
            url: event.context.cancel_ticket_url
          }).done(function(response) {
            orderComponent.set(event.keypath + '.cancelled_at', response.result.cancelled_at);
            orderComponent.set(event.keypath + '.cancelling', false);
          }).fail(function(response) {
            let errorMsg;
            if (response.readyState === 4) {
              if (response.status === 500) {
                errorMsg = "Server Error";
              }
              else {
                errorMsg = JSON.parse(response.responseText).error_description;
              }
            }
            else {
              errorMsg = "Unable to connect. Please try again later.";
            }
            orderComponent.set(event.keypath + '.cancelError', errorMsg);
            orderComponent.set(event.keypath + '.cancelling', false);
          });
        }
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
