
import {urlFor} from '../models/util.js';
import {FormView} from './form_view.js';
import {navigateTo} from '../views/main_admin.js';

export const PartialRefundOrderView = {
  render: function({ic_id, order_id}={}) {
    FormView.load({
      url: urlFor('partial_refund', {scope_ns: 'ic', scope_id: ic_id, resource: 'order', id: order_id, root: true}),
      title: 'Partial refund for order',
      onHide: function(){
        // TODO redirect to order
        navigateTo(urlFor('index', {scope_ns: 'ic', scope_id: ic_id, resource: 'orders', root: true}))
      },
      onSuccess: function(responseData){
        // TODO redirect to order
        navigateTo(urlFor('index', {scope_ns: 'ic', scope_id: ic_id, resource: 'orders', root: true}))
      }
    });
  }
}
