
import {DiscountPolicyModel} from '../models/admin_discount_policy.js';
import {DiscountPolicyTemplate} from '../templates/admin_discount_policy.html.js';
import {SideBarView} from './sidebar.js';

export const DiscountPolicyView = {
  render: function(config) {

    DiscountPolicyModel.fetch({
      url: DiscountPolicyModel.urlFor('index', {org_name: config.org_name})['path']
    }).done((remoteData) => {
      // Initial render
      console.log("DiscountPolicyModel", remoteData);
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: DiscountPolicyTemplate,
        data:  {
          org: remoteData.org_name,
          title: remoteData.title,
          discount_policies: remoteData.discount_policies
        }
      });

      SideBarView.render('discount-policies', {'org_name': remoteData.org_name});

      NProgress.done();

      $('#discount-policies-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200,
          largescreen: 1900
        }
      });

      main_ractive.on('addPolicy', function(event){
        //Show discount policy add form
      });

      main_ractive.on('editPolicy', function(event){
        //Show discount policy edit form
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
