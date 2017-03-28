
import {scrollToElement, getFormParameters, getCsrfToken, getErrorMsg} from '../models/util.js';
import {OrderModel} from '../models/admin_order.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';

export const OrderView = {
  render: function (config) {

    OrderModel.fetch({
      url: OrderModel.urlFor('index', {ic_id: config.id})['path']
    }).done((remoteData) => {
      // Initial render
      let orderComponent = new Ractive({
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

      $("#search-form").on("keypress", function (e) {
        if (e.which == 13) {
          return false;
        }
      });

      orderComponent.on('showDetails', function (event) {
        orderComponent.set({
        	//Close all other open side panels
        	'orders.*.showDetailsSlider': false,
        	'orders.*.showRefundForm': false,
        	//Show individual order
        	[event.keypath + '.loading']: true
        });
        NProgress.configure({ showSpinner: false}).start();
        let order_id = event.context.id;
        OrderModel.fetch({
          url: OrderModel.urlFor('view', {order_id: order_id})['path']
        }).done((remoteData) => {
        	let ractive_id = "#" + orderComponent.el.id;
        	NProgress.done();
          orderComponent.set({
          	[event.keypath + '.line_items']: remoteData.line_items,
          	[event.keypath + '.showDetailsSlider']: true,
          	[event.keypath + '.loading']: false
          });
          scrollToElement(ractive_id);
        });
      });

      orderComponent.on('hideDetails', function (event) {
        orderComponent.set(event.keypath + '.showDetailsSlider', false);
      });

      orderComponent.on('cancelTicket', function (event, method) {
        if (window.confirm("Are you sure you want to cancel this ticket?")) {
          orderComponent.set({
          	[event.keypath + '.cancel_error']: "",
          	[event.keypath + '.cancelling']: true
          });

          OrderModel.post({
            url: event.context.cancel_ticket_url
          }).done(function (response) {
            orderComponent.set({
            	[event.keypath + '.cancelled_at']: response.result.cancelled_at,
            	[event.keypath + '.cancelling']: false
            });
          }).fail(function (response) {
            let errorMsg = getErrorMsg(response);
            orderComponent.set({
            	[event.keypath + '.cancel_error']: errorMsg,
            	[event.keypath + '.cancelling']: false
            });
          });
        }
      });

      orderComponent.on('showRefundForm', function (event) {
      	let ractive_id = "#" + orderComponent.el.id;
        orderComponent.set({
        	//Close all other open side panels
        	'orders.*.showDetailsSlider': false,
        	'orders.*.showRefundForm': false,
        	//Show individual order
        	[event.keypath + '.showRefundForm']: true
        });
        scrollToElement(ractive_id);
      });

      orderComponent.on('refundOrder', function (event, method) {
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
          orderComponent.set({
          	[order + '.refund.errormsg.*']: "",
          	[order + '.refund.status']: ""
          });
          if (errors.length > 0) {
            orderComponent.set(order + '.refund.errormsg.'+ errors[0].name, errors[0].message);
          } else {
          	orderComponent.set(order + '.refund.errormsg.*', "");
            let formSelector = '#refund-form-' + orderId;

            if (window.confirm("Are you sure you want to refund this ticket?")) {
              orderComponent.set(order + '.refunding', true);
              OrderModel.post({
                url: refundUrl,
                data: getFormParameters(formSelector),
                json: false
              }).done(function (response) {
              	let refundDescription = orderComponent.get(order + '.refund.refund_description');
              	orderComponent.set({
              		[order + '.refunding']: false,
              		//Update the order net total
									[order + '.net_amount']: response.result.order_net_amount,
                	// Clear form
                	[order + '.refund.*']: "",
                	//Update refund status
                	[order + '.refund.status']: response.result.message
              	});
                //Add to refunds array
                orderComponent.push(order + '.refunds', {'refunded_at': response.result.refunded_at, 'refund_description': refundDescription, 'refund_amount': response.result.refund_amount});
              }).fail(function (response) {
                let errorMsg = getErrorMsg(response);
                orderComponent.set({
                	[order + '.refund.errormsg.refundError']: errorMsg,
                	[order + '.refunding']: false
               	});
              });
            }
          }
        });

        formValidator.setMessage('required', 'Please fill out this field');
        formValidator.setMessage('is_natural_no_zero', 'Please enter a numeric value greater than 0');
      });

      orderComponent.on('hideRefundForm', function (event) {
        orderComponent.set({
        	[event.keypath + '.showRefundForm']: false,
        	//Clear form
        	[event.keypath + '.refund.*']: ""
        });
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
