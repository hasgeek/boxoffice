import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const NewItemView = {
  render({ menuId } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'menu',
        scope_id: menuId,
        resource: 'item',
        root: true,
      }),
      title: 'New item',
      onHide() {
        navigateTo(
          urlFor('view', { resource: 'menu', id: menuId, root: true })
        );
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('view', {
            resource: 'item',
            id: responseData.result.item.id,
            root: true,
          })
        );
      },
    });
  },
};

export { NewItemView as default };
