
import {fetch, post, scrollToElement, urlFor} from '../models/util.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';

export const OrderView = {
  render: function(view, {ic_id}={}) {

    fetch({
      url: urlFor('index', {scope_ns: 'ic', scope_id: ic_id, resource: 'orders', root: true})
    }).done(({org_name, title, orders}) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data:  {
          title: title,
          orders: orders
        }
      });

      SideBarView.render('orders', {org_name, ic_id});

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

      main_ractive.on('showOrder', function(event){
        //Close all other open side panels
        main_ractive.set('orders.*.show_order', false);
        //Show individual order
        main_ractive.set(event.keypath + '.loading', true);
        NProgress.configure({ showSpinner: false}).start();
        let order_id = event.context.id;
        fetch({
          url: urlFor('view', {
            resource: 'order',
            id: order_id,
            root: true
          })
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.line_items', remoteData.line_items);
          main_ractive.set(event.keypath + '.show_order', true);
          NProgress.done();
          main_ractive.set(event.keypath + '.loading', false);
          let ractive_id = "#" + main_ractive.el.id;
          scrollToElement(ractive_id);
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
          post({
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
