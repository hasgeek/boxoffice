import { urlFor } from '../models/util.js';
import { FormView } from './form_view.js';
import { navigateTo } from '../views/main_admin.js';

export const EditItemView = {
  render: function ({ item_id } = {}) {
    FormView.load({
      url: urlFor('edit', { resource: 'item', id: item_id, root: true }),
      title: 'Edit item',
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
