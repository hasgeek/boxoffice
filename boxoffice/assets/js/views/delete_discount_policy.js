
import {urlFor} from '../models/util.js';
import {FormView} from './form_view.js';
import {navigateTo} from '../views/main_admin.js';

export const DeleteDiscountPolicyView = {
  render: function({org_name, id}={}) {
    FormView.load({
      url: urlFor('delete', {scope_ns: 'o', scope_id: org_name, resource: 'discount_policy', id: id, root: true}),
      title: 'Are you sure you want to delete this discount policy?',
      onHide: function(){
        navigateTo(urlFor('index', {scope_ns: 'o', scope_id: org_name, resource: 'discount_policy', root: true}))
      },
      onSuccess: function(responseData){
        navigateTo(urlFor('index', {scope_ns: 'o', scope_id: org_name, resource: 'discount_policy', root: true}))
      }
    });
  }
}
