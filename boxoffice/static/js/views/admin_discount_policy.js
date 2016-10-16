
import {OrgModel} from '../models/org.js';
import {DiscountPolicyModel} from '../models/admin_discount_policy.js';
import {DiscountPolicyTemplate} from '../templates/admin_discount_policy.html.js';
import {SideBarView} from './sidebar.js';

export const DiscountPolicyView = {
  render: function({org_name, search, page}={}) {
    let url;
    if (search) {
      url = DiscountPolicyModel.urlFor('search', {org_name, search, page})['path'];
    }
    else {
      url = DiscountPolicyModel.urlFor('index', {org_name, page})['path'];
    }

    DiscountPolicyModel.fetch({
      url: url
    }).done(({org_name, title, discount_policies, total_pages, paginated, current_page}) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: DiscountPolicyTemplate,
        data:  {
          org: org_name,
          title: title,
          discount_policies: discount_policies,
          paginated: paginated,
          total_pages: total_pages,
          current_page: current_page,
          pages: Array.from(Array(total_pages).keys()).map(x => ++x),
          items: '',
          show_add_policy_form: false,
          new_discount_policy: '',
          get_discounted_items: function(dp_items) {
            let discounted_items = dp_items.map(function(dp_item) {
              return dp_item.id;
            });
            return discounted_items.join(',');
          }
        },
        refresh: function(search='', page='') {
          let url;
          if (search) {
            url = DiscountPolicyModel.urlFor('search', {org_name, search, page})['path'];
          }
          else {
            url = DiscountPolicyModel.urlFor('index', {org_name, page})['path'];
          }
          NProgress.start();
          DiscountPolicyModel.fetch({
            url: url
          }).done((remoteData) => {
            main_ractive.set('discount_policies', remoteData.discount_policies);
            NProgress.done();
          });
          window.history.replaceState({reloadOnPop: true}, '', window.location.href);
          window.history.pushState({reloadOnPop: true}, '', url);
        }
      });

      SideBarView.render('discount-policies', {org_name});

      NProgress.done();

      let addFormFields =  function(is_price_based) {
        if (is_price_based) {
          $("#add-item").select2({
            placeholder: "Search a ticket",
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
            placeholder: "Search tickets",
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

      main_ractive.on('openNewPolicyForm', function(event) {
        main_ractive.set('show_add_policy_form', true);
        main_ractive.set('new_discount_policy.is_price_based', 1);
        main_ractive.set('new_discount_policy.discount_type', 1);
        addFormFields(main_ractive.get('new_discount_policy.is_price_based'));
      });

      main_ractive.on('policyChange', function(event) {
        main_ractive.set('new_discount_policy.is_price_based', parseInt(event.node.value, 10));
        addFormFields(main_ractive.get('new_discount_policy.is_price_based'));
      });

      main_ractive.on('policyTypeChange', function(event) {
        main_ractive.set('new_discount_policy.discount_type', event.node.value);
      });

      main_ractive.on('closeNewPolicyForm', function(event) {
        main_ractive.set('show_add_policy_form', false);
      });

      main_ractive.on('addNewPolicy', function(event) {
        var validation_config = [
          {
            name: 'title',
            rules: 'required'
          },
          {
            name: 'item_quantity_min',
            rules: 'required|numeric'
          },
          {
            name: 'price_title',
            rules: 'required'
          },
          {
            name: 'amount',
            rules: 'required|numeric'
          },
          {
            name: 'start_at',
            rules: 'required'
          },
          {
            name: 'end_at',
            rules: 'required'
          },
          {
            name: 'item',
            rules: 'required'
          },
          {
            name: 'percentage',
            rules: 'required|numeric'
          },
          {
            name: 'items',
            rules: 'required'
          }
        ];

        var policy_form_name = 'adding-new-policy-form';

        var form_validator = new FormValidator(policy_form_name, validation_config, function(errors, event) {
          event.preventDefault();
          main_ractive.set('new_discount_policy.errormsg', '');
          if (errors.length > 0) {
            main_ractive.set('new_discount_policy.errormsg.'+ errors[0].name, errors[0].message);
          }
          else {
            main_ractive.set('new_discount_policy.generate_policy_error', '');
            main_ractive.set('new_discount_policy.creatingPolicy', true);
            let new_policy_form = '#new-policy-form';

            DiscountPolicyModel.post({
              url: DiscountPolicyModel.urlFor('new', {org_name: main_ractive.get('org')})['path'],
              data: DiscountPolicyModel.convertFormToJSON(new_policy_form, ['items']),
              contentType: 'application/json'
            }).done((remoteData) => {
              main_ractive.set('discount_policies', [remoteData.result.discount_policy]);
              main_ractive.set('new_discount_policy.creatingPolicy', false);
              let url = DiscountPolicyModel.urlFor('search', {org_name: org_name, search: main_ractive.get('new_discount_policy.title')})['path'];
              window.history.replaceState({reloadOnPop: true}, '', window.location.href);
              window.history.pushState({reloadOnPop: true}, '', url);
              main_ractive.fire('closeNewPolicyForm');
            }).fail(function(response) {
              let error_msg;
              if (response.readyState === 4) {
                if(response.status === 500) {
                  error_msg = "Internal Server Error"
                }
                else {
                  error_msg = JSON.parse(response.responseText).message;
                }
              }
              if (response.readyState === 0) {
                error_msg = "Unable to connect. Please try again."
              }
              main_ractive.set('new_discount_policy.creatingPolicy', false);
              main_ractive.set('new_discount_policy.generate_policy_error', error_msg);
            });
          }
        });

        form_validator.setMessage('required', 'Please fill out the this field');

      });

      main_ractive.on('searchPolicy', function(event) {
        let search = event.node.value;
        if (search.length > 2) {
          main_ractive.refresh(search);
        }
        else if(search.length === 0) {
          main_ractive.refresh();
        }
      });

      main_ractive.on('paginate', function(event, page) {
        event.original.preventDefault();
        main_ractive.refresh('', page);
      })

      main_ractive.on('editPolicyForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', true);
        main_ractive.set(event.keypath + '.show_policy_form', true);
        main_ractive.set(event.keypath +  '.errormsg', '');
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
              callback(main_ractive.get(event.keypath + '.dp_items.0'));
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
              callback(main_ractive.get(event.keypath + '.dp_items'));
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
        var discount_policy = event.keypath;
        var discount_policy_id = event.context.id;

        var validation_config = [
          {
            name: 'title',
            rules: 'required'
          },
          {
            name: 'item_quantity_min',
            rules: 'required|numeric'
          },
          {
            name: 'price_title',
            rules: 'required'
          },
          {
            name: 'amount',
            rules: 'required|numeric'
          },
          {
            name: 'start_at',
            rules: 'required'
          },
          {
            name: 'end_at',
            rules: 'required'
          },
          {
            name: 'item',
            rules: 'required'
          },
          {
            name: 'percentage',
            rules: 'required|numeric'
          },
          {
            name: 'items',
            rules: 'required'
          }
        ];

        var policy_form_name = 'edit-policy-form-' + discount_policy_id;

        var form_validator = new FormValidator(policy_form_name, validation_config, function(errors, event) {
          event.preventDefault();
          main_ractive.set(discount_policy +  '.errormsg', '');
          if (errors.length > 0) {
            main_ractive.set(discount_policy +  '.errormsg.'+ errors[0].name, errors[0].message);
          }
          else {
            main_ractive.set(discount_policy + '.editingPolicy', true);
            let policy_form = '#policy-form-' + discount_policy_id;

            DiscountPolicyModel.post({
              url: DiscountPolicyModel.urlFor('edit', {discount_policy_id: discount_policy_id})['path'],
              data: DiscountPolicyModel.convertFormToJSON(policy_form, ["items"]),
              contentType: 'application/json'
            }).done((remoteData) => {
              main_ractive.set(discount_policy + '.editingPolicy', false);
              main_ractive.set(discount_policy, remoteData.result.discount_policy);
              main_ractive.set(discount_policy + '.show_policy_form', false);
              main_ractive.set(discount_policy + '.hide_edit_btn', false);
            }).fail(function(response) {
              let error_msg;
              if(response.status === 500) {
                error_msg = "Internal Server Error"
              }
              else {
                error_msg = JSON.parse(response.responseText).message;
              }
              if (response.readyState === 0) {
                error_msg = "Unable to connect. Please try again."
              }
              main_ractive.set(discount_policy + '.editingPolicy', false);
              main_ractive.set(discount_policy + '.edit_policy_error', error_msg);
              main_ractive.set(discount_policy + '.hide_edit_btn', false);
            });
          }
        });

        form_validator.setMessage('required', 'Please fill out the this field');

      });

      main_ractive.on('generateCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', true);
        main_ractive.set(event.keypath + '.generate_signed_coupon', false);
        main_ractive.set(event.keypath + '.show_add_coupon_form', true);
      });

      main_ractive.on('hidegenerateCouponForm', function(event) {
        main_ractive.set(event.keypath + '.hide_edit_btn', false);
        main_ractive.set(event.keypath + '.show_add_coupon_form', false);
      });

      main_ractive.on('listCoupons', function(event) {
        event.original.preventDefault();
        main_ractive.set(event.keypath + '.loadingCoupons', true);
        main_ractive.set(event.keypath + '.loading_coupon_error', '');
        let discount_policy_id = event.context.id;

        DiscountPolicyModel.fetch({
          url: DiscountPolicyModel.urlFor('list_coupons', {discount_policy_id: discount_policy_id})['path'],
          contentType: 'application/json'
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.coupons', remoteData.result.coupons);
          main_ractive.set(event.keypath + '.loadingCoupons', false);
          $('#list-coupons-' + discount_policy_id).modal('show');
          $('#coupons-list-' + discount_policy_id).footable();
          new Clipboard('.copy-coupons-list');
        }).fail(function(response) {
          let error_msg;
          if(response.status === 500) {
            error_msg = "Internal Server Error"
          }
          else {
            error_msg = JSON.parse(response.responseText).message;
          }
          if (response.readyState === 0) {
            error_msg = "Unable to connect. Please try again."
          }
          main_ractive.set(event.keypath + '.loadingCoupons', false);
          main_ractive.set(event.keypath + '.loading_coupon_error', error_msg);
        });

      });

      main_ractive.on('generateCoupon', function(event) {
        var discount_policy = event.keypath;
        var discount_policy_id = event.context.id;

        var validation_config = [
          {
            name: 'count',
            rules: 'required|numeric'
          },
          {
            name: 'usage_limit',
            rules: 'required|numeric'
          }
        ];

        var coupon_form_name = 'generate-coupon-form-' + discount_policy_id;

        var form_validator = new FormValidator(coupon_form_name, validation_config, function(errors, event) {
          event.preventDefault();
          main_ractive.set(discount_policy +  '.errormsg', '');
          if (errors.length > 0) {
            main_ractive.set(discount_policy +  '.errormsg.'+ errors[0].name, errors[0].message);
          }
          else {
            let coupon_form = '#new-coupon-' + discount_policy_id;
            main_ractive.set(discount_policy+ '.generatingCoupon', true);
            main_ractive.set(discount_policy + '.generate_coupon_error', '');
            DiscountPolicyModel.post({
              url: DiscountPolicyModel.urlFor('generate_coupon', {discount_policy_id: discount_policy_id})['path'],
              data: DiscountPolicyModel.convertFormToJSON(coupon_form, []),
              contentType: 'application/json'
            }).done((remoteData) => {
              main_ractive.set(discount_policy + '.coupons', remoteData.result.coupons);
              main_ractive.set(discount_policy + '.generatingCoupon', false);
              $('#generated-coupons-' + discount_policy_id).modal('show');
              new Clipboard('.copy-coupons');
            }).fail(function(response) {
              let error_msg;
              if (response.readyState === 4) {
                if(response.status === 500) {
                  error_msg = "Internal Server Error"
                }
                else {
                  error_msg = JSON.parse(response.responseText).error_description;
                }
              }
              if (response.readyState === 0) {
                error_msg = "Unable to connect. Please try again."
              }
              main_ractive.set(discount_policy + '.generatingCoupon', false);
              main_ractive.set(discount_policy + '.generate_coupon_error', error_msg);
            });
          }
        });

        form_validator.setMessage('required', 'Please fill out the this field');

      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
