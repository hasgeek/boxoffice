import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const DeleteDiscountPolicyView = {
  render({ accountName, id } = {}) {
    FormView.load({
      url: urlFor('delete', {
        scope_ns: 'o',
        scope_id: accountName,
        resource: 'discount_policy',
        id,
        root: true,
      }),
      title: 'Are you sure you want to delete this discount policy?',
      onHide() {
        navigateTo(
          urlFor('index', {
            scope_ns: 'o',
            scope_id: accountName,
            resource: 'discount_policy',
            root: true,
          })
        );
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('index', {
            scope_ns: 'o',
            scope_id: accountName,
            resource: 'discount_policy',
            root: true,
          })
        );
      },
    });
  },
};

export { DeleteDiscountPolicyView as default };
