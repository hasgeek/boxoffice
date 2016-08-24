
import {OrgModel} from '../models/org.js';
import {DiscountPolicyModel} from '../models/admin_discount_policy.js';
import {DiscountPolicyTemplate} from '../templates/admin_discount_policy.html.js';
import {SideBarView} from './sidebar.js';

export const DiscountPolicyView = {
  render: function(config) {

    DiscountPolicyModel.fetch({
      url: DiscountPolicyModel.urlFor('index', {org_name: config.org_name})['path']
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: DiscountPolicyTemplate,
        data:  {
          org: remoteData.org_name,
          title: remoteData.title,
          discount_policies: remoteData.discount_policies,
          items: '',
          show_add_policy_form: false,
          is_item_discounted: function(dp_items, item_id) {
            var discount_applicable;
            dp_items.forEach(function(dp_item) {
              if (item_id === dp_item.id) {
                discount_applicable = true;
              }
            });
            return discount_applicable;
          }
        },
      });

      SideBarView.render('discount-policies', {'org_name': remoteData.org_name});

      NProgress.done();

      main_ractive.on('addNewPolicyForm', function(event) {
        main_ractive.set('show_add_policy_form', true);
      });

      main_ractive.on('hideNewPolicyForm', function(event) {
        main_ractive.set('show_add_policy_form', false);
      });

      main_ractive.on('addNewPolicy', function(event) {
        event.original.preventDefault();
        main_ractive.set(event.keypath + '.addingPolicy', true);

        DiscountPolicyModel.post({
          url: DiscountPolicyModel.urlFor('new', {org_name: main_ractive.get('org')})['path']
        }).done((remoteData) => {
          console.log("remoteData",remoteData);
          main_ractive.set(event.keypath + '.show_add_policy_form', false);
        }).fail(function(response) {
          main_ractive.set(event.keypath + '.addingPolicy', false);
          main_ractive.set(event.keypath + '.add_policy_error', error_text);
        });

      });

      main_ractive.on('editPolicyForm', function(event) {
        main_ractive.set(event.keypath + '.loadingEditForm', true);

        OrgModel.fetch({
          url: OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path']
        }).done((remoteData) => {
          main_ractive.set('items', remoteData.items);
          main_ractive.set(event.keypath + '.loadingEditForm', false);
          main_ractive.set(event.keypath + '.show_policy_form', true);
          $('#add-items-' + event.context.id).multiselect({
            nonSelectedText: 'Items',
            numberDisplayed: 1,
            buttonWidth: '100%',
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            templates: {
              filter: '<li><div class="input-group input-group-sm"><div class="input-group-addon"><i class="fa fa-search"></i></div><input type="text" class="form-control" id="items-search" placeholder="Search">',
              filterClearBtn: '<div class="input-group-addon items-search-clear"><i class="fa fa-times"></i></div></div></li>'
            }
          });
        }).fail(function() {
          main_ractive.set(event.keypath + '.loadingEditForm', false);
        });

      });

      main_ractive.on('hideEditPolicy', function(event) {
        main_ractive.set(event.keypath + '.show_policy_form', false);
      });

      main_ractive.on('editPolicy', function(event) {
        event.original.preventDefault();
        main_ractive.set(event.keypath + '.editingPolicy', true);
        let discount_policy_id = event.context.id;

        DiscountPolicyModel.post({
          url: DiscountPolicyModel.urlFor('edit', {discount_policy_id: discount_policy_id})['path']
        }).done((remoteData) => {
          console.log("remoteData",remoteData);
          main_ractive.set(event.keypath + '.editingPolicy', false);
          main_ractive.set(event.keypath + '.show_policy_form', false);
        }).fail(function(response) {
          main_ractive.set(event.keypath + '.editingPolicy', false);
          main_ractive.set(event.keypath + '.edit_policy_error', error_text);
        });

      });

      main_ractive.on('generateCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', true);
        main_ractive.set(event.keypath + '.show_add_coupon_form', true);
      });

      main_ractive.on('hidegenerateCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', false);
        main_ractive.set(event.keypath + '.show_add_coupon_form', false);
      });


      main_ractive.on('generateCoupon', function(event) {
        event.original.preventDefault();
        main_ractive.set(event.keypath + '.generatingCoupon', true);
        main_ractive.set(event.keypath + '.usage', 1);
        let discount_policy_id = event.context.id;

        DiscountPolicyModel.post({
          url: DiscountPolicyModel.urlFor('generate_coupon', {discount_policy_id: discount_policy_id})['path']
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.generatingCoupon', false);
          main_ractive.set(event.keypath + '.coupons', remoteData.result.coupons);
        }).fail(function(response) {
          main_ractive.set(event.keypath + '.generatingCoupon', false);
          main_ractive.set(event.keypath + '.generate_coupon_error', error_text);
        });

      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
