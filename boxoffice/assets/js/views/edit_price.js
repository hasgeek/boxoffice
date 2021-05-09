import { urlFor } from '../models/util.js';
import { FormView } from './form_view.js';
import { navigateTo } from '../views/main_admin.js';

export const EditPriceView = {
  render: function ({ item_id, price_id } = {}) {
    FormView.load({
      url: urlFor('edit', {
        scope_ns: 'item',
        scope_id: item_id,
        resource: 'price',
        id: price_id,
        root: true,
      }),
      title: 'Edit price',
      onHide: function () {
        navigateTo(
          urlFor('view', { resource: 'item', id: item_id, root: true })
        );
      },
      onSuccess: function (responseData) {
        navigateTo(
          urlFor('view', { resource: 'item', id: item_id, root: true })
        );
      },
    });
  },
};
