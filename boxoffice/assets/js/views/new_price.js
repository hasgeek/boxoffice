/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const NewPriceView = {
  render({ ticketId } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'item',
        scope_id: ticketId,
        resource: 'price',
        root: true,
      }),
      title: 'New price',
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

export { NewPriceView as default };
