import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const ItemCollectionEditView = {
  render({ menuId } = {}) {
    FormView.load({
      url: urlFor('edit', { resource: 'menu', id: menuId, root: true }),
      title: 'Edit item collection',
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

export { ItemCollectionEditView as default };
