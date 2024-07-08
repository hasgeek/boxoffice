import { urlFor } from '../models/util';
import { FormView } from './form_view';
import { navigateTo } from './navigate';

export const NewTicketView = {
  render({ menuId } = {}) {
    FormView.load({
      url: urlFor('new', {
        scope_ns: 'menu',
        scope_id: menuId,
        resource: 'ticket',
        root: true,
      }),
      title: 'New ticket',
      onHide() {
        navigateTo(urlFor('view', { resource: 'menu', id: menuId, root: true }));
      },
      onSuccess(responseData) {
        navigateTo(
          urlFor('view', {
            resource: 'ticket',
            id: responseData.result.ticket.id,
            root: true,
          })
        );
      },
    });
  },
};

export { NewTicketView as default };
