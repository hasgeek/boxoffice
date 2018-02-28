
import {urlFor} from '../models/util.js';
import {FormView} from './form_view.js';
import {navigateTo} from '../views/main_admin.js';

export const NewPriceView = {
  render: function({item_id}={}) {
    FormView.load({
      url: urlFor('new', {scope_ns: 'item', scope_id: item_id, resource: 'price', root: true}),
      title: 'New price',
      onHide: function(){
        navigateTo(urlFor('view', {resource: 'item', id: item_id, root: true}))
      },
      onSuccess: function(responseData){
        navigateTo(urlFor('view', {resource: 'item', id: item_id, root: true}))
      }
    });
  }
}
