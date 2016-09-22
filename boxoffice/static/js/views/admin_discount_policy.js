
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
          new_discount_policy: '',
          get_discounted_items: function(dp_items) {
            var discounted_items = dp_items.map(function(dp_item) {
              return dp_item.id;
            });
            return discounted_items.join(',');
          }
        },
        policyChange: function(event) {
          main_ractive.set('new_discount_policy.discount_type', event.node.value);
        },
        refresh: function(complete) {
          NProgress.start();
          DiscountPolicyModel.fetch({
            url: DiscountPolicyModel.urlFor('index', {org_name: config.org_name})['path']
          }).done((remoteData) => {
            main_ractive.set('discount_policies', remoteData.discount_policies);
            NProgress.done();
            complete();
          });
        },
        closeNewPolicyForm: function() {
          main_ractive.set('new_discount_policy.creatingPolicy', false);
          main_ractive.set('show_add_policy_form', false);
        }
      });

      SideBarView.render('discount-policies', {'org_name': remoteData.org_name});

      NProgress.done();

      let addFormFields =  function(is_price_based) {
        if (is_price_based) {
          $("#add-item").select2({
            placeholder: "Search a item",
            minimumInputLength: 3,
            ajax: {
                url: OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path'],
                dataType: 'json',
                quietMillis: 250,
                data: function (term) {
                  return {
                    search: term
                  };
                },
                results: function (data) {
                  return {
                    results: data.items
                  };
                },
                cache: true
            },
            formatResult: function(item) {
              var markup = '<p>' + item.title + '</p>';
              return markup;
            },
            formatSelection: function(item) {
              return item.title;
            },
            dropdownCssClass: "bigdrop"
          });

          $('#start_date').daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            timePicker: true,
            timePickerSeconds: true,
            timePicker24Hour: true,
            opens: 'left',
            locale: {
              format: 'DD MM YYYY H:mm:ss'
            }
          });

          $('#end_date').daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            timePicker: true,
            timePickerSeconds: true,
            timePicker24Hour: true,
            opens: 'left',
            locale: {
              format: 'DD MM YYYY H:mm:ss'
            }
          });
        }
        else {
          $("#add-items").select2({
            placeholder: "Search a item",
            minimumInputLength: 3,
            multiple: true,
            ajax: {
              url: OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path'],
              dataType: 'json',
              quietMillis: 250,
              data: function (term) {
                return {
                  search: term
                };
              },
              results: function (data) {
                return {
                  results: data.items 
                };
              },
              cache: true
            },
            formatResult: function(item) {
              let markup = '<p>' + item.title + '</p>';
              return markup;
            },
            formatSelection: function(item) {
              return item.title;
            },
            dropdownCssClass: "bigdrop"
          });
        }
      }

      main_ractive.observe('new_discount_policy.is_price_based', function(is_price_based) {
        if (typeof is_price_based != 'undefined') {
          addFormFields(main_ractive.get('new_discount_policy.is_price_based'));
        }
      }, { defer: true });

      main_ractive.on('addNewPolicyForm', function(event) {
        main_ractive.set('show_add_policy_form', true);
        main_ractive.set('new_discount_policy.is_price_based', true);
      });

      main_ractive.on('hideNewPolicyForm', function(event) {
        main_ractive.set('show_add_policy_form', false);
        main_ractive.set('new_discount_policy.is_price_based', false);
      });

      main_ractive.on('addNewPolicy', function(event) {
        event.original.preventDefault();
        main_ractive.set('new_discount_policy.generate_policy_error', '');
        main_ractive.set('new_discount_policy.creatingPolicy', true);
        let new_policy_form = '#new-policy-form';

        DiscountPolicyModel.post({
          url: DiscountPolicyModel.urlFor('new', {org_name: main_ractive.get('org')})['path'],
          data: DiscountPolicyModel.convertFormToJSON(new_policy_form, ['items']),
          contentType: 'application/json'
        }).done((remoteData) => {
          main_ractive.refresh(main_ractive.closeNewPolicyForm);
        }).fail(function(response) {
          let error_msg;
          if (response.readyState === 4) {
            error_msg = JSON.parse(response.responseText).message;
          }
          if (response.readyState === 0) {
            error_msg = "Unable to connect. Please try again."
          }
          main_ractive.set('new_discount_policy.creatingPolicy', false);
          main_ractive.set('new_discount_policy.generate_policy_error', error_msg);
        });

      });

      main_ractive.on('editPolicyForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', true);
        main_ractive.set(event.keypath + '.show_policy_form', true);
        let discount_policy_id = event.context.id;

        if (main_ractive.get(event.keypath + '.is_price_based')) {
          $('#start_date_' + discount_policy_id).daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            timePicker: true,
            timePickerSeconds: true,
            timePicker24Hour: true,
            opens: 'left',
            locale: {
              format: 'DD MM YYYY HH:mm:ss'
            }
          });

          $('#end_date_' + discount_policy_id).daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            timePicker: true,
            timePickerSeconds: true,
            timePicker24Hour: true,
            opens: 'left',
            locale: {
              format: 'DD MM YYYY HH:mm:ss'
            }
          });

          $('#add-item-' + discount_policy_id).select2({
            placeholder: "Search a item",
            minimumInputLength: 3,
            ajax: {
                url: OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path'],
                dataType: 'json',
                quietMillis: 250,
                data: function (term) {
                    return {
                        search: term,
                    };
                },
                results: function (data) {
                    return { results: data.items };
                },
                cache: true
            },
            formatResult: function(item) {
              var markup = '<p>' + item.title + '</p>';
              return markup;
            },
            formatSelection: function(item) {
              return item.title;
            },
            initSelection: function(element, callback) {
              // TODO: Get dp_items title
              // console.log("dp_items", main_ractive.get(event.keypath + '.dp_items'));
              $.ajax(OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path'] + "?search=", {
                  dataType: "json"
              }).done(function(data) { callback(data.items[0]); });
            },
            dropdownCssClass: "bigdrop"
          });
        }
        else {
          $("#add-items-" + discount_policy_id).select2({
            placeholder: "Search a item",
            minimumInputLength: 3,
            multiple: true,
            ajax: {
              url: OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path'],
              dataType: 'json',
              quietMillis: 250,
              data: function (term) {
                return {
                  search: term
                };
              },
              results: function (data) {
                return {
                  results: data.items
                };
              },
              cache: true
            },
            formatResult: function(item) {
              let markup = '<p>' + item.title + '</p>';
              return markup;
            },
            formatSelection: function(item) {
              return item.title;
            },
            initSelection: function(element, callback) {
              // TODO: Get dp_items title
              // console.log("dp_items", main_ractive.get(event.keypath + '.dp_items'));
              $.ajax(OrgModel.urlFor('view_items', {org_name: main_ractive.get('org')})['path'] + "?search=", {
                  dataType: "json"
              }).done(function(data) { callback(data.items); });
            },
            dropdownCssClass: "bigdrop"
          });
        }
      });

      main_ractive.on('hideEditPolicy', function(event) {
        main_ractive.set(event.keypath + '.show_policy_form', false);
        main_ractive.set(event.keypath + '.hide_edit_btn', false);
      });

      main_ractive.on('editPolicy', function(event) {
        event.original.preventDefault();
        main_ractive.set(event.keypath + '.editingPolicy', true);
        let discount_policy_id = event.context.id;
        let policy_form = '#policy-form-' + discount_policy_id;

        DiscountPolicyModel.post({
          url: DiscountPolicyModel.urlFor('edit', {discount_policy_id: discount_policy_id})['path'],
          data: DiscountPolicyModel.convertFormToJSON(policy_form, ["items"]),
          contentType: 'application/json'
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.editingPolicy', false);
          main_ractive.set(event.keypath, remoteData.result.discount_policy);
          main_ractive.set(event.keypath + '.show_policy_form', false);
          main_ractive.set(event.keypath + '.hide_edit_btn', false);
        }).fail(function(response) {
          let error_msg;
          if (response.readyState === 4) {
            error_msg = JSON.parse(response.responseText).message;
          }
          if (response.readyState === 0) {
            error_msg = "Unable to connect. Please try again."
          }
          main_ractive.set(event.keypath + '.editingPolicy', false);
          main_ractive.set(event.keypath + '.edit_policy_error', error_msg);
          main_ractive.set(event.keypath + '.hide_edit_btn', false);
        });

      });

      main_ractive.on('generateCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', true);
        main_ractive.set(event.keypath + '.generate_signed_coupon', false);
        main_ractive.set(event.keypath + '.show_add_coupon_form', true);
      });

      main_ractive.on('generateSignedCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', true);
        main_ractive.set(event.keypath + '.generate_signed_coupon', true);
        main_ractive.set(event.keypath + '.show_add_coupon_form', true);
      });

      main_ractive.on('hidegenerateCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', false);
        main_ractive.set(event.keypath + '.show_add_coupon_form', false);
      });


      main_ractive.on('generateCoupon', function(event) {
        event.original.preventDefault();
        main_ractive.set(event.keypath + '.generatingCoupon', true);
        let discount_policy_id = event.context.id;
        let coupon_form = '#new-coupon-' + discount_policy_id;

        DiscountPolicyModel.post({
          url: DiscountPolicyModel.urlFor('generate_coupon', {discount_policy_id: discount_policy_id})['path'],
          data: DiscountPolicyModel.convertFormToJSON(coupon_form, []),
          contentType: 'application/json'
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.generatingCoupon', false);
          if (main_ractive.get(event.keypath + '.coupons')) {
            Array.prototype.push.apply(main_ractive.get(event.keypath + '.coupons'), remoteData.result.coupons);
          }
          else {
            main_ractive.set(event.keypath + '.coupons', remoteData.result.coupons);
          }
          main_ractive.set(event.keypath + '.hide_edit_btn', false);
          main_ractive.set(event.keypath + '.show_add_coupon_form', false);
          $('#coupons-' + discount_policy_id).modal('show');
        }).fail(function(response) {
          let error_msg;
          if (response.readyState === 4) {
            error_msg = JSON.parse(response.responseText).error_description;
          }
          if (response.readyState === 0) {
            error_msg = "Unable to connect. Please try again."
          }
          main_ractive.set(event.keypath + '.generatingCoupon', false);
          main_ractive.set(event.keypath + '.generate_coupon_error', error_msg);
        });

      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
