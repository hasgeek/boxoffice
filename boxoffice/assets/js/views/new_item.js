
import {urlFor} from '../models/util.js';
import {FormView} from './form_view.js';
import {navigateTo} from '../views/main_admin.js';

export const NewItemView = {
  render: function({ic_id}={}) {
    FormView.load({
      url: urlFor('new', {scope_ns: 'ic', scope_id: ic_id, resource: 'item', root: true}),
      title: 'New item',
      onHide: function(){
        navigateTo(urlFor('view', {resource: 'ic', id: ic_id, root: true}))
      },
      onSuccess: function(responseData){
        navigateTo(urlFor('view', {resource: 'item', id: responseData.result.item.id, root: true}))
      }
    });
  }
}
