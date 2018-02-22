
import {DetailView, urlFor} from '../models/util.js';
import {navigateTo} from '../views/main_admin.js';

export const ItemCollectionNewView = {
  render: function({org_name}={}) {
    DetailView.load({
      url: urlFor('new', {scope_ns: 'o', scope_id: org_name, resource: 'ic', root: true}),
      title: 'New item collection',
      handleForm: true,
      onSuccess: function(responseData){
        console.log(responseData);
        navigateTo(urlFor('view', {resource: 'ic', id: responseData.result.item_collection.id, root: true}))
      }
    })
  }
}
