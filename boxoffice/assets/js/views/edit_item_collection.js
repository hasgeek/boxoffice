import { urlFor } from '../models/util.js';
import { FormView } from './form_view.js';
import { navigateTo } from '../views/main_admin.js';

export const ItemCollectionEditView = {
  render: function ({ ic_id } = {}) {
    FormView.load({
      url: urlFor('edit', { resource: 'ic', id: ic_id, root: true }),
      title: 'Edit item collection',
      onHide: function () {
        navigateTo(urlFor('view', { resource: 'ic', id: ic_id, root: true }));
      },
      onSuccess: function (responseData) {
        navigateTo(urlFor('view', { resource: 'ic', id: ic_id, root: true }));
      },
    });
  },
};
