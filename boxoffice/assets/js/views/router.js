import { IndexView } from './index';
import { OrgView } from './org';
import { OrgReportView } from './org_report_admin';
import { DiscountPolicyView } from './discount_policy_admin';
import { DeleteDiscountPolicyView } from './discount_policy_delete';
import { MenuView } from './menu';
import { MenuNewView } from './menu_new';
import { MenuEditView } from './menu_edit';
import { OrdersView } from './orders_admin';
import { OrderView } from './order_admin';
import { ReportView } from './report_admin';
import { TicketView } from './ticket_admin';
import { NewTicketView } from './ticket_new';
import { EditTicketView } from './ticket_edit';
import { NewPriceView } from './price_new';
import { EditPriceView } from './price_edit';
import { NewCategoryView } from './category_new';
import { EditCategoryView } from './category_edit';
import { PartialRefundOrderView } from './order_partial_refund';

const Backbone = require('backbone');

export const Router = Backbone.Router.extend({
  url_root: '/admin/',
  routes: {
    '': 'index',
    'o/:accountName': 'org',
    'o/:accountName/reports': 'org_report',
    'o/:accountName/discount_policy': 'discount_policy',
    'o/:accountName/discount_policy/:id/delete': 'delete_discount_policy',
    'o/:accountName/discount_policy?:params': 'discount_policy',
    'menu/:menuId': 'menu',
    'menu/:menuId/reports': 'report',
    'o/:accountName/menu/new': 'new_menu',
    'menu/:menuId/edit': 'edit_menu',
    'menu/:menuId/orders': 'orders',
    'o/:accountName/order/:orderReceiptNo': 'order',
    'menu/:menuId/ticket/new': 'new_ticket',
    'ticket/:ticketId/edit': 'edit_ticket',
    'ticket/:ticketId': 'ticket',
    'ticket/:ticketId/price/new': 'new_price',
    'ticket/:ticketId/price/:priceId/edit': 'edit_price',
    'menu/:menuId/category/new': 'new_category',
    'menu/:menuId/category/:categoryId/edit': 'edit_category',
    'menu/:menuId/order/:orderId/partial_refund': 'partial_refund_order',
  },
  index() {
    IndexView.render();
  },
  org(accountName) {
    OrgView.render({ accountName });
  },
  org_report(accountName) {
    OrgReportView.render({ accountName });
  },
  discount_policy(accountName, { search, page, size } = {}) {
    DiscountPolicyView.render({ accountName, search, page, size });
  },
  delete_discount_policy(accountName, id) {
    DeleteDiscountPolicyView.render({ accountName, id });
  },
  menu(menuId) {
    MenuView.render({ menuId });
  },
  new_menu(accountName) {
    if (window.boxofficeFirstLoad) {
      OrgView.render({ accountName });
    }
    MenuNewView.render({ accountName });
  },
  edit_menu(menuId) {
    if (window.boxofficeFirstLoad) {
      MenuView.render({ menuId });
    }
    MenuEditView.render({ menuId });
  },
  new_ticket(menuId) {
    if (window.boxofficeFirstLoad) {
      MenuView.render({ menuId });
    }
    NewTicketView.render({ menuId });
  },
  edit_ticket(ticketId) {
    if (window.boxofficeFirstLoad) {
      TicketView.render({ ticketId });
    }
    EditTicketView.render({ ticketId });
  },
  new_price(ticketId) {
    if (window.boxofficeFirstLoad) {
      TicketView.render({ ticketId });
    }
    NewPriceView.render({ ticketId });
  },
  edit_price(ticketId, priceId) {
    if (window.boxofficeFirstLoad) {
      TicketView.render({ ticketId });
    }
    EditPriceView.render({ ticketId, priceId });
  },
  new_category(menuId) {
    if (window.boxofficeFirstLoad) {
      MenuView.render({ menuId });
    }
    NewCategoryView.render({ menuId });
  },
  edit_category(menuId, categoryId) {
    if (window.boxofficeFirstLoad) {
      MenuView.render({ menuId });
    }
    EditCategoryView.render({ menuId, categoryId });
  },
  orders(menuId) {
    OrdersView.render({ menuId });
  },
  order(accountName, orderReceiptNo) {
    OrderView.render({ accountName, orderReceiptNo });
  },
  report(menuId) {
    ReportView.render({ menuId });
  },
  ticket(ticketId) {
    TicketView.render({ ticketId });
  },
  partial_refund_order(menuId, orderId) {
    if (window.boxofficeFirstLoad) {
      MenuView.render({ menuId });
    }
    PartialRefundOrderView.render({ menuId, orderId });
  },
  // eslint-disable-next-line no-underscore-dangle
  _extractParameters(route, fragment) {
    const result = route.exec(fragment).slice(1);
    if (result[result.length - 1]) {
      const paramString = result[result.length - 1].split('&');
      const params = {};
      paramString.forEach((value) => {
        if (value) {
          const [paramKey, paramValue] = value.split('=');
          params[paramKey] = paramValue;
        }
      });
      result[result.length - 1] = params;
    }
    return result;
  },
});

export { Router as default };
