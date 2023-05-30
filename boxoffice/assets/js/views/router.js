import { IndexView } from './index';
import { OrgView } from './org';
import { OrgReportView } from './admin_org_report';
import { DiscountPolicyView } from './admin_discount_policy';
import { DeleteDiscountPolicyView } from './delete_discount_policy';
import { ItemCollectionView } from './item_collection';
import { ItemCollectionNewView } from './new_item_collection';
import { ItemCollectionEditView } from './edit_item_collection';
import { OrdersView } from './admin_orders';
import { OrderView } from './admin_order';
import { ReportView } from './admin_report';
import { ItemView } from './admin_item';
import { NewItemView } from './new_item';
import { EditItemView } from './edit_item';
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
    'menu/:menuId': 'item_collection',
    'menu/:menuId/reports': 'report',
    'o/:accountName/menu/new': 'new_item_collection',
    'menu/:menuId/edit': 'edit_item_collection',
    'menu/:menuId/orders': 'orders',
    'o/:accountName/order/:orderReceiptNo': 'order',
    'menu/:menuId/item/new': 'new_item',
    'item/:ticketId/edit': 'edit_item',
    'item/:ticketId': 'item',
    'item/:ticketId/price/new': 'new_price',
    'item/:ticketId/price/:priceId/edit': 'edit_price',
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
  item_collection(menuId) {
    ItemCollectionView.render({ menuId });
  },
  new_item_collection(accountName) {
    if (window.boxofficeFirstLoad) {
      OrgView.render({ accountName });
    }
    ItemCollectionNewView.render({ accountName });
  },
  edit_item_collection(menuId) {
    if (window.boxofficeFirstLoad) {
      ItemCollectionView.render({ menuId });
    }
    ItemCollectionEditView.render({ menuId });
  },
  new_item(menuId) {
    if (window.boxofficeFirstLoad) {
      ItemCollectionView.render({ menuId });
    }
    NewItemView.render({ menuId });
  },
  edit_item(ticketId) {
    if (window.boxofficeFirstLoad) {
      ItemView.render({ ticketId });
    }
    EditItemView.render({ ticketId });
  },
  new_price(ticketId) {
    if (window.boxofficeFirstLoad) {
      ItemView.render({ ticketId });
    }
    NewPriceView.render({ ticketId });
  },
  edit_price(ticketId, priceId) {
    if (window.boxofficeFirstLoad) {
      ItemView.render({ ticketId });
    }
    EditPriceView.render({ ticketId, priceId });
  },
  new_category(menuId) {
    if (window.boxofficeFirstLoad) {
      ItemCollectionView.render({ menuId });
    }
    NewCategoryView.render({ menuId });
  },
  edit_category(menuId, categoryId) {
    if (window.boxofficeFirstLoad) {
      ItemCollectionView.render({ menuId });
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
  item(ticketId) {
    ItemView.render({ ticketId });
  },
  partial_refund_order(menuId, orderId) {
    if (window.boxofficeFirstLoad) {
      ItemCollectionView.render({ menuId });
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
