
import {scrollToElement, getFormParameters, getCsrfToken} from '../models/util.js';
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
          orders: remoteData.orders,
          getCsrfToken: function () {
            //Defined as a function so that it is called every time the form is opened
            return getCsrfToken()
          }
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
        OrderModel.fetch({
          url: OrderModel.urlFor('view', {order_id: order_id})['path']
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

      main_ractive.on('showRefundForm', function(event){
        //Close all other open side panels
        main_ractive.set('orders.*.showRefundForm', false);
        //Show individual order
        main_ractive.set(event.keypath + '.showRefundForm', true);
        let order_id = event.context.id;
        let ractive_id = "#" + main_ractive.el.id;
        scrollToElement(ractive_id);
      });

      main_ractive.on('refundOrder', function(event, method) {
        let order = event.keypath,
          orderId = event.context.id,
          refundFormName = 'order-refund-form-' + orderId,
          refundUrl = event.context.refund_url,
          validationConfig = [{
              name: 'amount',
              rules: 'required|is_natural_no_zero'
            },
            {
              name: 'internal_note',
              rules: 'required'
            },
            {
              name: 'refund_description',
              rules: 'required'
            },
            {
              name: 'note_to_user',
              rules: 'required'
            }
          ];

        let formValidator = new FormValidator(refundFormName, validationConfig, function (errors, event) {
          event.preventDefault();
          main_ractive.set(order + '.refund.errormsg.*', "");
          main_ractive.set(order + '.refund.status', "");
          if (errors.length > 0) {
            main_ractive.set(order + '.refund.errormsg.'+ errors[0].name, errors[0].message);
          } else {
          	main_ractive.set(order + '.refund.errormsg.*', "");
            let formSelector = '#refund-form-' + orderId;

            if (window.confirm("Are you sure you want to refund this ticket?")) {
              main_ractive.set(order + '.refunding', true);
              OrderModel.post({
                url: refundUrl,
                data: getFormParameters(formSelector),
                json: false
              }).done(function(response) {
              	main_ractive.set(order + '.refunding', false);
              	//Update refund status
                main_ractive.set(order + '.refund.status', response.result.message);
              	//Update the order net total
                main_ractive.set(order + '.net_amount', response.result.order_net_amount);
                //Add to refunds array
                main_ractive.push(order + '.refunds', {'refunded_at': response.result.refunded_at, 'refund_description': main_ractive.get(order + '.refund.refund_description'), 'refund_amount': response.result.refund_amount});
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
                main_ractive.set(order + '.refund.errormsg.refundError', errorMsg);
                main_ractive.set(order + '.refunding', false);
              });
            }
          }
        });

        formValidator.setMessage('required', 'Please fill out the this field');
        formValidator.setMessage('is_natural_no_zero', 'Please enter a numberic value greater than 0');
      });

      main_ractive.on('hideRefundForm', function(event){
        //Show individual order
        main_ractive.set(event.keypath + '.showRefundForm', false);
        main_ractive.set(event.keypath + '.refund.*', "");
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
