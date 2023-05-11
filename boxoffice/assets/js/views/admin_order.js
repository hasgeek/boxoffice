import { Util, fetch, post, urlFor, setPageTitle } from '../models/util';
import { OrderTemplate } from '../templates/admin_order.html';
import { navigateTo } from './navigate';

const NProgress = require('nprogress');
const Ractive = require('ractive');

export const OrderView = {
  render({ accountName, orderReceiptNo } = {}) {
    fetch({
      url: urlFor('view', {
        scope_ns: 'o',
        scope_id: accountName,
        resource: 'order',
        id: orderReceiptNo,
        root: true,
      }),
    })
      .done(({ account, menu, order, line_items: lineItems }) => {
        // Initial render
        const orderComponent = new Ractive({
          el: '#main-content-area',
          template: OrderTemplate,
          data: {
            order,
            menu,
            lineItems,
            formatDateTime(dateTimeString) {
              return Util.formatDateTime(dateTimeString);
            },
            formatToIndianRupee(amount) {
              return Util.formatToIndianRupee(amount);
            },
          },
        });

        orderComponent.on('cancelTicket', (event, method) => {
          if (window.confirm('Are you sure you want to cancel this ticket?')) {
            orderComponent.set(`${event.keypath}.cancel_error`, '');
            orderComponent.set(`${event.keypath}.cancelling`, true);

            post({
              url: event.context.cancel_ticket_url,
            })
              .done((response) => {
                orderComponent.set(
                  `${event.keypath}.cancelled_at`,
                  response.result.cancelled_at
                );
                orderComponent.set(`${event.keypath}.cancelling`, false);
              })
              .fail((response) => {
                let errorText;
                if (response.readyState === 4) {
                  if (response.status === 500) {
                    errorText = 'Server Error';
                  } else {
                    errorText = JSON.parse(
                      response.responseText
                    ).error_description;
                  }
                } else {
                  errorText = 'Unable to connect. Please try again later.';
                }
                orderComponent.set(`${event.keypath}.cancel_error`, errorText);
                orderComponent.set(`${event.keypath}.cancelling`, false);
              });
          }
        });

        orderComponent.on('closeOrder', (event, method) => {
          if (window.history.length <= 2) {
            navigateTo(`/admin/menu/${menu.id}/orders`);
          } else {
            window.history.back();
          }
        });

        // SideBarView.render('org_reports', {org.name, org.title});
        setPageTitle('Orders', account.title);
        NProgress.done();
      })
      .fail(() => {
        window.history.back();
      });
  },
};

export { OrderView as default };
