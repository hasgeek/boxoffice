import { urlFor } from '../models/util.js';
import { FormView } from './form_view.js';
import { navigateTo } from '../views/main_admin.js';

export const ItemCollectionNewView = {
  render: function ({ org_name } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'o',
        scope_id: org_name,
        resource: 'ic',
        root: true,
      }),
      title: 'New item collection',
      onHide: function () {
        navigateTo(urlFor('view', { resource: 'o', id: org_name, root: true }));
      },
      onSuccess: function (responseData) {
        navigateTo(
          urlFor('view', {
            resource: 'ic',
            id: responseData.result.item_collection.id,
            root: true,
          })
        );
      },
    });
  },
};
