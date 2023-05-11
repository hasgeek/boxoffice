/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const PartialRefundOrderView = {
  render({ menuId, orderId } = {}) {
    FormView.load({
      url: urlFor('partial_refund', {
        scope_ns: 'menu',
        scope_id: menuId,
        resource: 'order',
        id: orderId,
        root: true,
      }),
      title: 'Partial refund for order',
      onHide() {
        // TODO redirect to order
        navigateTo(
          urlFor('index', {
            scope_ns: 'menu',
            scope_id: menuId,
            resource: 'orders',
            root: true,
          })
        );
      },
      onSuccess(responseData) {
        // TODO redirect to order
        navigateTo(
          urlFor('index', {
            scope_ns: 'menu',
            scope_id: menuId,
            resource: 'orders',
            root: true,
          })
        );
      },
    });
  },
};

export { PartialRefundOrderView as default };
