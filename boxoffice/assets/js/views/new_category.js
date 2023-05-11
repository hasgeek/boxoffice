/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const NewCategoryView = {
  render({ menuId } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'menu',
        scope_id: menuId,
        resource: 'category',
        root: true,
      }),
      title: 'New category',
      onHide() {
        navigateTo(
          urlFor('view', { resource: 'menu', id: menuId, root: true })
        );
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('view', { resource: 'menu', id: menuId, root: true })
        );
      },
    });
  },
};

export { NewCategoryView as default };
