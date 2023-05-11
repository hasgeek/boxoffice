/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const EditPriceView = {
  render({ ticketId, priceId } = {}) {
    FormView.load({
      url: urlFor('edit', {
        scope_ns: 'item',
        scope_id: ticketId,
        resource: 'price',
        id: priceId,
        root: true,
      }),
      title: 'Edit price',
      onHide() {
        navigateTo(
          urlFor('view', { resource: 'item', id: ticketId, root: true })
        );
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('view', { resource: 'item', id: ticketId, root: true })
        );
      },
    });
  },
};

export { EditPriceView as default };
