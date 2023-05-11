/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const EditItemView = {
  render({ ticketId } = {}) {
    FormView.load({
      url: urlFor('edit', { resource: 'item', id: ticketId, root: true }),
      title: 'Edit item',
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

export { EditItemView as default };
