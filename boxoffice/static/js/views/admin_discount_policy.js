
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
    }).done(({org_name, title, discount_policies, total_pages, paginated, current_page}) => {
      // Initial render
      let discountPolicyComponent = new Ractive({
        el: '#main-content-area',
        template: DiscountPolicyTemplate,
        data:  {
          org: org_name,
          title: title,
          discountPolicies: discount_policies,
          paginated: paginated,
          totalPages: total_pages,
          currentPage: current_page,
          items: '',
          showAddPolicyForm: false,
          newDiscountPolicy: '',
          searchText: search,
          formValidationConfig: [
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
          ],
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
          } else {
            url = DiscountPolicyModel.urlFor('index', {org_name, page})['path'];
          }
          NProgress.start();
          DiscountPolicyModel.fetch({
            url: url
          }).done((remoteData) => {
            discountPolicyComponent.set('discountPolicies', remoteData.discount_policies);
            discountPolicyComponent.set('paginated', remoteData.paginated);
            discountPolicyComponent.set('totalPages', remoteData.total_pages);
            discountPolicyComponent.set('currentPage', remoteData.current_page);
            discountPolicyComponent.set('pages', discountPolicyComponent.get_pages(remoteData.total_pages));
            NProgress.done();
          });
          window.history.replaceState({reloadOnPop: true}, '', window.location.href);
          window.history.pushState({reloadOnPop: true}, '', url);
        },
        get_pages: function (totalPages) {
          var pages = [];
          for (var i=1; i<= totalPages; i++) {
            pages.push(i);
          }
          return pages;
        },
        paginate: function (event, page) {
          event.original.preventDefault();
          discountPolicyComponent.refresh('', page);
        },
        clearSearchField: function() {
          discountPolicyComponent.set('searchText', "");
        },
        addFormFields: function(isPriceBased, discountPolicy) {
          console.log("addFormFields", isPriceBased, discountPolicy);
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
              minimumInputLength: 3,
              placeholder: {
                id: "-1", // the value of the option
                title: "Search tickets"
              },
              ajax: {
                url: OrgModel.urlFor('view_items', {org_name: discountPolicyComponent.get('org')})['path'],
                dataType: 'json',
                data: function (params) {
                  return {
                    search: params.term
                  };
                },
                processResults: function (data) {
                  return {
                    results: data.items
                  };
                },
                cache: true
              },
              escapeMarkup: function (markup) { return markup; },
              templateResult: function(item) {
                let markup = '<p>' + item.title + '</p>';
                return markup;
              },
              templateSelection: function(item) {
                return item.title;
              }
            });

            $(startDateSelector).daterangepicker({
              singleDatePicker: true,
              showDropdowns: true,
              timePicker: true,
              timePickerSeconds: true,
              timePicker24Hour: true,
              opens: 'left',
              locale: {
                format: 'D MMM YYYY H:mm:ss'
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
                format: 'D MMM YYYY H:mm:ss'
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
              minimumInputLength: 3,
              multiple: true,
              placeholder: 'Search tickets',
              ajax: {
                url: OrgModel.urlFor('view_items', {org_name: discountPolicyComponent.get('org')})['path'],
                dataType: 'json',
                data: function (params) {
                  return {
                    search: params.term
                  };
                },
                processResults: function (data) {
                  console.log("processResults", data.items);
                  return {
                    results: data.items
                  };
                },
                cache: true
              },
              escapeMarkup: function (markup) { return markup; },
              templateResult: function(item) {
                let markup = '<p>' + item.title + '</p>';
                return markup;
              },
              templateSelection: function(item) {
                return item.title;
              }
            });
          }
        },
        showNewPolicyForm: function(event) {
          discountPolicyComponent.set('showAddPolicyForm', true);
          discountPolicyComponent.set('newDiscountPolicy.is_price_based', 1);
          discountPolicyComponent.set('newDiscountPolicy.discount_type', 1);
          discountPolicyComponent.addFormFields(discountPolicyComponent.get('newDiscountPolicy.is_price_based'));
        },
        policyChange: function(event) {
          discountPolicyComponent.set('newDiscountPolicy.is_price_based', parseInt(event.node.value, 10));
          discountPolicyComponent.addFormFields(discountPolicyComponent.get('newDiscountPolicy.is_price_based'));
        },
        policyTypeChange: function(event) {
          discountPolicyComponent.set('newDiscountPolicy.discount_type', event.node.value);
        },
        addNewPolicy: function(event) {
          let formName = 'adding-new-policy-form';

          let formValidator = new FormValidator(formName, discountPolicyComponent.get('formValidationConfig'), function(errors, event) {
            event.preventDefault();
            discountPolicyComponent.set('newDiscountPolicy.errormsg', "");
            if (errors.length > 0) {
              discountPolicyComponent.set('newDiscountPolicy.errormsg.'+ errors[0].name, errors[0].message);
            }
            else {
              discountPolicyComponent.set('newDiscountPolicy.errorMsg', "");
              discountPolicyComponent.set('newDiscountPolicy.creatingPolicy', true);
              let formSelector = '#new-policy-form';

              DiscountPolicyModel.post({
                url: DiscountPolicyModel.urlFor('new', {org_name: discountPolicyComponent.get('org')})['path'],
                data: DiscountPolicyModel.getFormParameters(formSelector)
              }).done((remoteData) => {
                discountPolicyComponent.set('discountPolicies', [remoteData.result.discount_policy]);
                discountPolicyComponent.set('searchText', discountPolicyComponent.get('newDiscountPolicy.title'));
                discountPolicyComponent.set('newDiscountPolicy.creatingPolicy', false);
                discountPolicyComponent.hideNewPolicyForm();
                discountPolicyComponent.set('newDiscountPolicy', '');
              }).fail(function(response) {
                let errorMsg;
                if (response.readyState === 4) {
                  if(response.status === 500) {
                    errorMsg = "Internal Server Error";
                  }
                  else {
                    let errorDescription = JSON.parse(response.responseText).error_description;
                    for (let error in errorDescription) {
                      errorMsg += "<p>" + errorDescription[error] + "</p>";
                    }
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
        },
        validateCodeBase: function(event, dp="newDiscountPolicy") {
          //If there is change in discount_code_base value, then validate it
          if(event.node.value !== event.context.discount_code_base) {
            DiscountPolicyModel.fetch({
              url: DiscountPolicyModel.urlFor('lookup')['path'] + "?discount_code_base=" + event.node.value
            }).done((response) => {
              discountPolicyComponent.set(dp + '.errormsg.discount_code_base', "");
            }).fail(function(response) {
              let errorMsg;
              if (response.readyState === 4 && response.status !== 500) {
                errorMsg = JSON.parse(response.responseText).error_description;
                discountPolicyComponent.set(dp + '.errormsg.discount_code_base', errorMsg);
              }
            });
          }
        },
        hideNewPolicyForm: function(event) {
          discountPolicyComponent.set('showAddPolicyForm', false);
        },
        showEditPolicyForm: function(event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.hideEditBtn', true);
          discountPolicyComponent.set(discountPolicy + '.showPolicyForm', true);
          discountPolicyComponent.set(discountPolicy +  '.errormsg', '');
          discountPolicyComponent.addFormFields(discountPolicyComponent.get(discountPolicy + '.is_price_based'), discountPolicy);
        },
        editPolicy: function(event) {
          let discountPolicy = event.keypath,
            dpId = event.context.id,
            policyFormName = 'edit-policy-form-' + dpId;

          let formValidator = new FormValidator(policyFormName, discountPolicyComponent.get('formValidationConfig'), function(errors, event) {
            event.preventDefault();
            discountPolicyComponent.set(discountPolicy +  '.errormsg', "");
            if (errors.length > 0) {
              discountPolicyComponent.set(discountPolicy +  '.errormsg.'+ errors[0].name, errors[0].message);
            }
            else {
              discountPolicyComponent.set(discountPolicy + '.editingPolicy', true);
              let formSelector = '#policy-form-' + dpId;

              DiscountPolicyModel.post({
                url: DiscountPolicyModel.urlFor('edit', {discount_policy_id: dpId})['path'],
                data: DiscountPolicyModel.getFormParameters(formSelector)
              }).done((remoteData) => {
                discountPolicyComponent.set(discountPolicy + '.editingPolicy', false);
                discountPolicyComponent.set(discountPolicy, remoteData.result.discount_policy);
                discountPolicyComponent.set(discountPolicy + '.showPolicyForm', false);
                discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
                DiscountPolicyModel.scrollToElement('#dp-' + dpId);
              }).fail(function(response) {
                let errorMsg = "";
                if (response.status === 500) {
                  errorMsg = "Internal Server Error"
                }
                else {
                  let errorDescription = JSON.parse(response.responseText).error_description;
                  for (let error in errorDescription) {
                    errorMsg += '<p>' + errorDescription[error] + '</p>';
                  }
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

        },
        hideEditPolicyForm: function(event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.showPolicyForm', false);
          discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
        },
        showCouponForm: function(event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.hideEditBtn', true);
          discountPolicyComponent.set(discountPolicy + '.count', 1);
          discountPolicyComponent.set(discountPolicy + '.showCouponForm', true);
        },
        generateCoupon: function(event) {
          let discountPolicy = event.keypath,
            dpId = event.context.id,
            validationConfig = [
              {
                name: 'count',
                rules: 'required|numeric'
              },
              {
                name: 'usage_limit',
                rules: 'required|numeric'
              }
            ],
            couponFormName = 'generate-coupon-form-' + dpId;

          let formValidator = new FormValidator(couponFormName, validationConfig, function(errors, event) {
            event.preventDefault();
            discountPolicyComponent.set(discountPolicy +  '.errormsg', '');
            if (errors.length > 0) {
              discountPolicyComponent.set(discountPolicy +  '.errormsg.'+ errors[0].name, errors[0].message);
            }
            else {
              let formSelector = '#new-coupon-' + dpId;
              discountPolicyComponent.set(discountPolicy+ '.generatingCoupon', true);
              discountPolicyComponent.set(discountPolicy + '.generateCouponErrorMsg', "");

              DiscountPolicyModel.post({
                url: DiscountPolicyModel.urlFor('generate_coupon', {discount_policy_id: dpId})['path'],
                data: DiscountPolicyModel.getFormParameters(formSelector)
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
                    let errorDescription = JSON.parse(response.responseText).error_description;
                    for (let error in errorDescription) {
                      errorMsg += '<p>' + errorDescription[error] + '</p>';
                    }
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
        },
        hideCouponForm: function(event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.hideEditBtn', false);
          discountPolicyComponent.set(discountPolicy + '.showCouponForm', false);
        },
        getCouponList: function(event) {
          event.original.preventDefault();
          let discountPolicy = event.keypath;
          let dpId = event.context.id;
          discountPolicyComponent.set(discountPolicy + '.loadingCoupons', true);
          discountPolicyComponent.set(discountPolicy+ '.loadingCouponErrorMsg', "");

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
            if (response.readyState === 0) {
              errorMsg = "Unable to connect. Please try again."
            }
            discountPolicyComponent.set(discountPolicy + '.loadingCoupons', false);
            discountPolicyComponent.set(discountPolicy + '.loadingCouponErrorMsg', errorMsg);
          });

        },
        oncomplete: function() {

          discountPolicyComponent.observe('searchText', function(searchText, prevSearchText) {
            if (searchText.length > 2) {
              discountPolicyComponent.refresh(searchText);
            }
            else if(searchText.length === 0 && prevSearchText) {
              discountPolicyComponent.refresh();
            }
          });

          discountPolicyComponent.set('pages', discountPolicyComponent.get_pages(discountPolicyComponent.get('totalPages')));

        }
      });

      SideBarView.render('discount-policies', {org_name});

      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
