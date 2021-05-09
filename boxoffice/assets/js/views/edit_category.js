import { urlFor } from '../models/util.js';
import { FormView } from './form_view.js';
import { navigateTo } from '../views/main_admin.js';

export const EditCategoryView = {
  render: function ({ ic_id, category_id } = {}) {
    FormView.load({
      url: urlFor('edit', {
        scope_ns: 'ic',
        scope_id: ic_id,
        resource: 'category',
        id: category_id,
        root: true,
      }),
      title: 'Edit category',
      onHide: function () {
        navigateTo(urlFor('view', { resource: 'ic', id: ic_id, root: true }));
      },
      onSuccess: function (responseData) {
        navigateTo(urlFor('view', { resource: 'ic', id: ic_id, root: true }));
      },
    });
  },
};
