import { urlFor } from '../models/util.js';
import { FormView } from './form_view.js';
import { navigateTo } from '../views/main_admin.js';

export const NewCategoryView = {
  render: function ({ ic_id } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'ic',
        scope_id: ic_id,
        resource: 'category',
        root: true,
      }),
      title: 'New category',
      onHide: function () {
        navigateTo(urlFor('view', { resource: 'ic', id: ic_id, root: true }));
      },
      onSuccess: function (responseData) {
        navigateTo(urlFor('view', { resource: 'ic', id: ic_id, root: true }));
      },
    });
  },
};
