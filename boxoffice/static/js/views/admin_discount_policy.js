
import {scrollToElement} from '../models/util.js';
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
    }).done(({org_name, title, discount_policies}) => {
      // Initial render
      window.discountPolicyComponent = new Ractive({
        el: '#main-content-area',
        template: DiscountPolicyTemplate,
        data:  {
          org: org_name,
          title: title,
          discountPolicies: discount_policies,
          items: '',
          showAddPolicyForm: false,
          newDiscountPolicy: '',
          searchText: '',
          getDiscountedItems: function(dpItems) {
            let discountedItems = dpItems.map(function(dpItem) {
              return dpItem.id;
            });
            return discountedItems.join(',');
          },
          getCsrfToken: function() {
            return document.head.querySelector("[name=csrf-token]").content;
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
            discountPolicyComponent.set('discountPolicies', remoteData.discount_policies);
            NProgress.done();
          });
          window.history.replaceState({reloadOnPop: true}, '', window.location.href);
          window.history.pushState({reloadOnPop: true}, '', url);
        }
      });

      SideBarView.render('discount-policies', {org_name});

      NProgress.done();

      let formValidationConfig = [
        {
          name: 'title',
          rules: 'required|max_length[250]'
        },
        {
          name: 'is_price_based',
          rules: 'required'
        },
        {
          name: 'discount_type',
          rules: 'required'
        },
        {
          name: 'discount_code_base',
          rules: 'required|max_length[20]'
        },
        {
          name: 'bulk_coupon_usage_limit',
          rules: 'required|numeric'
        },
        {
          name: 'item_quantity_min',
          rules: 'required|numeric'
        },
        {
          name: 'price_title',
          rules: 'required|max_length[250]'
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
          name: 'percentage',
          rules: 'required|numeric'
        },
        {
          name: 'items',
          rules: 'required'
        }
      ];

      let addFormFields =  function(isPriceBased, discountPolicy) {

        if (isPriceBased) {
          let addItemSelector;
          let startDateSelector;
          let endDateSelector;

          if(discountPolicy) {
            let discount_policy_id = discountPolicyComponent.get(discountPolicy + '.id');
            addItemSelector = "#add-item-" + discount_policy_id;
            startDateSelector = "#start-date-" + discount_policy_id;
            endDateSelector = "#end-date-" + discount_policy_id;
          }
          else {
            addItemSelector = "#add-item";
            startDateSelector = "#start-date";
            endDateSelector = "#end-date";
          }

          $(addItemSelector).select2({
            placeholder: "Search a ticket",
            minimumInputLength: 3,
            ajax: {
                url: OrgModel.urlFor('view_items', {org_name: discountPolicyComponent.get('org')})['path'],
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
            initSelection: function(element, callback) {
              if(discountPolicy) {
                callback(discountPolicyComponent.get(discountPolicy + '.dp_items.0'));
              }
            },
            dropdownCssClass: "bigdrop"
          });

          $(startDateSelector).daterangepicker({
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

          $(endDateSelector).daterangepicker({
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
          let addItemsSelector;

          if(discountPolicy) {
            let dpId = discountPolicyComponent.get(discountPolicy + '.id');
            addItemsSelector = "#add-items-" + dpId;
          }
          else {
            addItemsSelector = "#add-items";
          }
          
          $(addItemsSelector).select2({
            placeholder: "Search tickets",
            minimumInputLength: 3,
            multiple: true,
            ajax: {
              url: OrgModel.urlFor('view_items', {org_name: discountPolicyComponent.get('org')})['path'],
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
              if(discountPolicy) {
                callback(discountPolicyComponent.get(discountPolicy + '.dp_items'));
              }
            },
            dropdownCssClass: "bigdrop"
          });
        }
      };

      discountPolicyComponent.on('openNewPolicyForm', function(event) {
        discountPolicyComponent.set('showAddPolicyForm', true);
        discountPolicyComponent.set('newDiscountPolicy.is_price_based', 1);
        discountPolicyComponent.set('newDiscountPolicy.discount_type', 1);
        addFormFields(discountPolicyComponent.get('newDiscountPolicy.is_price_based'));
      });

      discountPolicyComponent.on('policyChange', function(event) {
        discountPolicyComponent.set('newDiscountPolicy.is_price_based', parseInt(event.node.value, 10));
        addFormFields(discountPolicyComponent.get('newDiscountPolicy.is_price_based'));
      });
      
      discountPolicyComponent.on('policyTypeChange', function(event) {
        discountPolicyComponent.set('newDiscountPolicy.discount_type', event.node.value);
      });

      discountPolicyComponent.on('closeNewPolicyForm', function(event) {
        discountPolicyComponent.set('showAddPolicyForm', false);
      });

      discountPolicyComponent.on('addNewPolicy', function(event) {
        var formName = 'adding-new-policy-form';

        var formValidator = new FormValidator(formName, formValidationConfig, function(errors, event) {
          event.preventDefault();
          discountPolicyComponent.set('newDiscountPolicy.errormsg', '');
          if (errors.length > 0) {
            discountPolicyComponent.set('newDiscountPolicy.errormsg.'+ errors[0].name, errors[0].message);
          }
          else {
            discountPolicyComponent.set('newDiscountPolicy.errorMsg', '');
            discountPolicyComponent.set('newDiscountPolicy.creatingPolicy', true);
            let formSelector = '#new-policy-form';

            DiscountPolicyModel.post({
              url: DiscountPolicyModel.urlFor('new', {org_name: discountPolicyComponent.get('org')})['path'],
              data: DiscountPolicyModel.getFormParameters(formSelector, ['items'])
            }).done((remoteData) => {
              discountPolicyComponent.set('discountPolicies', [remoteData.result.discount_policy]);
              discountPolicyComponent.set('newDiscountPolicy.creatingPolicy', false);
              discountPolicyComponent.set('searchText', discountPolicyComponent.get('newDiscountPolicy.title'));
              discountPolicyComponent.fire('closeNewPolicyForm');
              discountPolicyComponent.set('newDiscountPolicy', '');
            }).fail(function(response) {
              let errorMsg;
              if (response.readyState === 4) {
                if(response.status === 500) {
                  errorMsg = "Internal Server Error";
                }
                else {
                  errorMsg = JSON.parse(response.responseText).error_description;
                }
              }
              if (response.readyState === 0) {
                errorMsg = "Unable to connect. Please try again.";
              }
              discountPolicyComponent.set('newDiscountPolicy.creatingPolicy', false);
              discountPolicyComponent.set('newDiscountPolicy.errorMsg', errorMsg);
            });
          }
        });

        formValidator.setMessage('required', 'Please fill out the this field');
        formValidator.setMessage('numeric', 'Please enter a numberic value');

      });

      discountPolicyComponent.observe('searchText', function(searchText) {
        if (searchText.length > 2) {
          discountPolicyComponent.refresh(searchText);
        }
        else if(searchText.length === 0) {
          discountPolicyComponent.refresh();
        }
      });

      discountPolicyComponent.on('clearSearchField', function() {
        discountPolicyComponent.set('searchText', '');
      });

      discountPolicyComponent.on('editPolicyForm', function(event) {
        let discountPolicy = event.keypath;
        discountPolicyComponent.set(discountPolicy + '.hideEditBtn', true);
        discountPolicyComponent.set(discountPolicy + '.showPolicyForm', true);
        discountPolicyComponent.set(discountPolicy +  '.errormsg', '');
        addFormFields(discountPolicyComponent.get(discountPolicy + '.is_price_based'), discountPolicy);
      });

      discountPolicyComponent.on('hideEditPolicy', function(event) {
        let discountPolicy = event.keypath;
        discountPolicyComponent.set(discountPolicy + '.showPolicyForm', false);
        discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
      });

      discountPolicyComponent.on('editPolicy', function(event) {
        var discountPolicy = event.keypath;
        var dpId = event.context.id;
        var policyFormName = 'edit-policy-form-' + dpId;

        var formValidator = new FormValidator(policyFormName, formValidationConfig, function(errors, event) {
          event.preventDefault();
          discountPolicyComponent.set(discountPolicy +  '.errormsg', '');
          if (errors.length > 0) {
            discountPolicyComponent.set(discountPolicy +  '.errormsg.'+ errors[0].name, errors[0].message);
          }
          else {
            discountPolicyComponent.set(discountPolicy + '.editingPolicy', true);
            let formSelector = '#policy-form-' + dpId;

            DiscountPolicyModel.post({
              url: DiscountPolicyModel.urlFor('edit', {discount_policy_id: dpId})['path'],
              data: DiscountPolicyModel.getFormParameters(formSelector, ['items'])
            }).done((remoteData) => {
              discountPolicyComponent.set(discountPolicy + '.editingPolicy', false);
              discountPolicyComponent.set(discountPolicy, remoteData.result.discount_policy);
              discountPolicyComponent.set(discountPolicy + '.showPolicyForm', false);
              discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
              DiscountPolicyModel.scrollToElement('#dp-' + dpId);
            }).fail(function(response) {
              let errorMsg;
              if (response.status === 500) {
                errorMsg = "Internal Server Error"
              }
              else {
                errorMsg = JSON.parse(response.responseText).error_description;
              }
              if (response.readyState === 0) {
                errorMsg = "Unable to connect. Please try again."
              }
              discountPolicyComponent.set(discountPolicy + '.editingPolicy', false);
              discountPolicyComponent.set(discountPolicy + '.errorMsg', errorMsg);
              discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
            });
          }
        });

        formValidator.setMessage('required', 'Please fill out the this field');
        formValidator.setMessage('numeric', 'Please enter a numberic value');

      });

      discountPolicyComponent.on('generateCouponForm', function(event) {
        let discountPolicy = event.keypath;
        discountPolicyComponent.set(discountPolicy + '.hideEditBtn', true);
        // discountPolicyComponent.set(event.keypath + '.generate_signed_coupon', false);
        discountPolicyComponent.set(discountPolicy + '.count', 1);
        discountPolicyComponent.set(discountPolicy + '.showCouponForm', true);
      });

      discountPolicyComponent.on('hidegenerateCouponForm', function(event) {
        let discountPolicy = event.keypath;
        discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
        discountPolicyComponent.set(discountPolicy + '.showCouponForm', false);
      });

      discountPolicyComponent.on('listCoupons', function(event) {
        event.original.preventDefault();
        let discountPolicy = event.keypath;
        let dpId = event.context.id;
        discountPolicyComponent.set(discountPolicy + '.loadingCoupons', true);
        discountPolicyComponent.set(discountPolicy+ '.loadingCouponErrorMsg', '');

        DiscountPolicyModel.fetch({
          url: DiscountPolicyModel.urlFor('list_coupons', {discount_policy_id: dpId})['path'],
          contentType: 'application/json'
        }).done((remoteData) => {
          discountPolicyComponent.set(discountPolicy + '.coupons', remoteData.result.coupons);
          discountPolicyComponent.set(discountPolicy + '.loadingCoupons', false);
          $('#list-coupons-' + dpId).modal('show');
          $('#coupons-list-' + dpId).footable();
          new Clipboard('.copy-coupons-list');
        }).fail(function(response) {
          let errorMsg;
          if(response.status === 500) {
            errorMsg = "Internal Server Error"
          }
          else {
            errorMsg = JSON.parse(response.responseText).message;
          }
          if (response.readyState === 0) {
            errorMsg = "Unable to connect. Please try again."
          }
          discountPolicyComponent.set(discountPolicy + '.loadingCoupons', false);
          discountPolicyComponent.set(discountPolicy + '.loadingCouponErrorMsg', errorMsg);
        });

      });

      discountPolicyComponent.on('generateCoupon', function(event) {
        var discountPolicy = event.keypath;
        var dpId = event.context.id;

        var validationConfig = [
          {
            name: 'count',
            rules: 'required|numeric'
          },
          {
            name: 'usage_limit',
            rules: 'required|numeric'
          }
        ];

        var couponFormName = 'generate-coupon-form-' + dpId;

        var formValidator = new FormValidator(couponFormName, validationConfig, function(errors, event) {
          event.preventDefault();
          discountPolicyComponent.set(discountPolicy +  '.errormsg', '');
          if (errors.length > 0) {
            discountPolicyComponent.set(discountPolicy +  '.errormsg.'+ errors[0].name, errors[0].message);
          }
          else {
            let formSelector = '#new-coupon-' + dpId;
            discountPolicyComponent.set(discountPolicy+ '.generatingCoupon', true);
            discountPolicyComponent.set(discountPolicy + '.generateCouponErrorMsg', '');

            DiscountPolicyModel.post({
              url: DiscountPolicyModel.urlFor('generate_coupon', {discount_policy_id: dpId})['path'],
              data: DiscountPolicyModel.getFormParameters(formSelector, [])
            }).done((remoteData) => {
              discountPolicyComponent.set(discountPolicy + '.coupons', remoteData.result.coupons);
              discountPolicyComponent.set(discountPolicy + '.generatingCoupon', false);
              $('#generated-coupons-' + dpId).modal('show');
              new Clipboard('.copy-coupons');
            }).fail(function(response) {
              let errorMsg;
              if (response.readyState === 4) {
                if(response.status === 500) {
                  errorMsg = "Internal Server Error"
                }
                else {
                  errorMsg = JSON.parse(response.responseText).error_description;
                }
              }
              if (response.readyState === 0) {
                errorMsg = "Unable to connect. Please try again."
              }
              discountPolicyComponent.set(discountPolicy + '.generatingCoupon', false);
              discountPolicyComponent.set(discountPolicy + '.generateCouponErrorMsg', errorMsg);
            });            
          }
        });

        formValidator.setMessage('required', 'Please fill out the this field');

      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
