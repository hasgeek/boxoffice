import { IndexView } from './index';
import { OrgView } from './org';
import { OrgReportView } from './admin_org_report';
import { DiscountPolicyView } from './admin_discount_policy';
import { DeleteDiscountPolicyView } from './delete_discount_policy';
import { MenuView } from './item_collection';
import { MenuNewView } from './new_item_collection';
import { MenuEditView } from './edit_item_collection';
import { OrdersView } from './admin_orders';
import { OrderView } from './admin_order';
import { ReportView } from './admin_report';
import { TicketView } from './admin_item';
import { NewTicketView } from './new_item';
import { EditTicketView } from './edit_item';
import { NewPriceView } from './new_price';
import { EditPriceView } from './edit_price';
import { NewCategoryView } from './new_category';
import { EditCategoryView } from './edit_category';
import { PartialRefundOrderView } from './partial_refund_order';

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
