/* eslint-disable no-unused-vars */
import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const EditTicketView = {
  render({ ticketId } = {}) {
    FormView.load({
      url: urlFor('edit', {
        resource: 'ticket',
        id: ticketId,
        root: true,
      }),
      title: 'Edit ticket',
      onHide() {
        navigateTo(
          urlFor('view', { resource: 'ticket', id: ticketId, root: true })
        );
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('view', { resource: 'ticket', id: ticketId, root: true })
        );
      },
    });
  },
};

export { EditTicketView as default };
