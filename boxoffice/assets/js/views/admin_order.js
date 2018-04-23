
var NProgress = require('nprogress');
var Ractive = require('ractive');
import {Util, fetch, post, urlFor, setPageTitle} from '../models/util.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';
import {navigateTo} from '../views/main_admin.js';

export const OrderView = {
  render: function({org_name, order_receipt_no}={}) {
    fetch({
      url: urlFor('view', {scope_ns: 'o', scope_id: org_name, resource: 'order', id: order_receipt_no, root: true})
    }).done(({org, ic, order, line_items}) => {
      // Initial render
      window.orderComponent = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data:  {
          order: order,
          ic: ic,
          line_items: line_items,
          formatDateTime: function (dateTimeString) {
            return Util.formatDateTime(dateTimeString);
          },
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          }
        }
      });

      orderComponent.on('cancelTicket', function(event, method) {
        if (window.confirm("Are you sure you want to cancel this ticket?")) {
          orderComponent.set(event.keypath + '.cancel_error', "");
          orderComponent.set(event.keypath + '.cancelling', true);

          post({
            url: event.context.cancel_ticket_url
          }).done(function(response) {
            orderComponent.set(event.keypath + '.cancelled_at', response.result.cancelled_at);
            orderComponent.set(event.keypath + '.cancelling', false);
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
            orderComponent.set(event.keypath + '.cancel_error', error_text);
            orderComponent.set(event.keypath + '.cancelling', false);
          });
        }
      });

      orderComponent.on('closeOrder', function(event, method) {
        if (window.history.length <= 2) {
          navigateTo(`/admin/ic/${ic.id}/orders`);
        } else {
          window.history.back();
        }
      });

      // SideBarView.render('org_reports', {org.name, org.title});
      setPageTitle("Orders", org.title);
      NProgress.done();
    }).fail(function(){
      window.history.back();
    });
  }
};
