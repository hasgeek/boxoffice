import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const ItemCollectionNewView = {
  render({ accountName } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'o',
        scope_id: accountName,
        resource: 'menu',
        root: true,
      }),
      title: 'New item collection',
      onHide() {
        navigateTo(
          urlFor('view', { resource: 'o', id: accountName, root: true })
        );
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('view', {
            resource: 'menu',
            id: responseData.result.item_collection.id,
            root: true,
          })
        );
      },
    });
  },
};

export { ItemCollectionNewView as default };
