
import {DetailView, urlFor} from '../models/util.js';
import {navigateTo} from '../views/main_admin.js';

export const ItemCollectionEditView = {
  render: function({ic_id}={}) {
    DetailView.load({
      url: urlFor('edit', {resource: 'ic', id: ic_id, root: true}),
      title: 'Edit item collection',
      handleForm: true,
      onSuccess: function(responseData){
        navigateTo(urlFor('view', {resource: 'ic', id: ic_id, root: true}))
      }
    })
  }
}
