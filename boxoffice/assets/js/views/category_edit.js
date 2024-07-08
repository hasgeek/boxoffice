/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const EditCategoryView = {
  render({ menuId, categoryId } = {}) {
    FormView.load({
      url: urlFor('edit', {
        scope_ns: 'menu',
        scope_id: menuId,
        resource: 'category',
        id: categoryId,
        root: true,
      }),
      title: 'Edit category',
      onHide() {
        navigateTo(urlFor('view', { resource: 'menu', id: menuId, root: true }));
      },
      onSuccess(responseData) {
        navigateTo(urlFor('view', { resource: 'menu', id: menuId, root: true }));
      },
    });
  },
};

export { EditCategoryView as default };
