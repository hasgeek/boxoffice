
import {fetch, post, scrollToElement, getFormParameters, getCsrfToken, updateBrowserHistory, urlFor} from '../models/util.js';
import {DiscountPolicyTemplate} from '../templates/admin_discount_policy.html.js';
import {SideBarView} from './sidebar.js';

export const DiscountPolicyView = {
  render: function (view, {org_name, search, page}={}) {
    let url;
    if (search) {
      url = urlFor('search', {
        scope_ns: 'o',
        scope_id: org_name,
        resource: 'discount_policy',
        root: true,
        search: search,
        page: page
      });
    } else {
      url = urlFor('index', {
        scope_ns: 'o',
        scope_id: org_name,
        resource: 'discount_policy',
        root: true,
        page: page
      });
    }

    const DEFAULT = {
      showForm: true,
      hideForm: false,
      showLoader: true,
      hideLoader: false,
      priceBasedDiscount: 1,
      couponBasedDiscount: 1,
      usageCount: 1,
      empty: ""
    };

    fetch({
      url: url
    }).done(({org_name, title, discount_policies, currency, total_pages, paginated, current_page}) => {
      // Initial render
      let discountPolicyComponent = new Ractive({
        el: '#main-content-area',
        template: DiscountPolicyTemplate,
        data:  {
          org: org_name,
          title: title,
          discountPolicies: discount_policies,
          currency: currency,
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
          getDiscountedItems: function (dpItems) {
            return dpItems.map(item => item.id).join(',')
          },
          getCsrfToken: function () {
            //Defined as a function so that it is called every time the form is opened
            return getCsrfToken()
          }
        },
        refresh: function (search='', page='') {
          let url;
          if (search) {
            url = urlFor('search', {
              scope_ns: 'o',
              scope_id: org_name,
              resource: 'discount_policy',
              root: true,
              search: search,
              page: page
            });
          } else {
            url = urlFor('index', {
              scope_ns: 'o',
              scope_id: org_name,
              resource: 'discount_policy',
              root: true,
              page: page
            });
          }

          NProgress.start();
          fetch({
            url: url
          }).done((remoteData) => {
            discountPolicyComponent.set({
              'discountPolicies': remoteData.discount_policies,
              'paginated': remoteData.paginated,
              'totalPages': remoteData.total_pages,
              'currentPage': remoteData.current_page,
              'pages': _.range(1, remoteData.total_pages + 1)
            });
            NProgress.done();
            updateBrowserHistory(window.location.href, url);
          });
          scrollToElement("#" + discountPolicyComponent.el.id);
        },
        paginate: function (event, page) {
          event.original.preventDefault();
          discountPolicyComponent.refresh(DEFAULT.empty, page);
        },
        clearSearchField: function () {
          discountPolicyComponent.set('searchText', DEFAULT.empty);
        },
        addFormFields: function (isPriceBased, discountPolicy) {
          if (isPriceBased) {
            let addItemSelector;
            let startDateSelector;
            let endDateSelector;

            if (discountPolicy) {
              let discount_policy_id = discountPolicyComponent.get(discountPolicy + '.id');
              addItemSelector = "#add-item-" + discount_policy_id;
              startDateSelector = "#start-date-" + discount_policy_id;
              endDateSelector = "#end-date-" + discount_policy_id;
            } else {
              addItemSelector = "#add-item";
              startDateSelector = "#start-date";
              endDateSelector = "#end-date";
            }

            $(addItemSelector).select2({
              minimumInputLength: 3,
              placeholder: {
                id: "-1",
                title: "Search tickets"
              },
              ajax: {
                url: urlFor('index', {
                  scope_ns: 'o',
                  scope_id: org_name,
                  resource: 'items',
                  root: true
                }),
                dataType: 'json',
                data: function (params) {
                  return {
                    search: params.term
                  };
                },
                processResults: function (data) {
                  return {
                    results: data.result.items
                  };
                },
              },
              // Do not want to escape markup since html is displayed in the results
              escapeMarkup: function (markup) { return markup; },
              templateResult: function(item) {
                return '<p>' + item.title + '</p>';
              },
              templateSelection: function (item) {
                return item.title;
              }
            });

            $(startDateSelector).daterangepicker({
              singleDatePicker: true,
              showDropdowns: true,
              timePicker: true,
              timePicker24Hour: true,
              opens: 'left',
              locale: {
                format: 'YYYY-MM-DD H:mm'
              }
            });

            $(endDateSelector).daterangepicker({
              singleDatePicker: true,
              showDropdowns: true,
              timePicker: true,
              timePicker24Hour: true,
              opens: 'left',
              locale: {
                format: 'YYYY-MM-DD H:mm'
              }
            });
          } else {
            let addItemsSelector;

            if (discountPolicy) {
              let dpId = discountPolicyComponent.get(discountPolicy + '.id');
              addItemsSelector = "#add-items-" + dpId;
            } else {
              addItemsSelector = "#add-items";
            }

            $(addItemsSelector).select2({
              minimumInputLength: 3,
              multiple: true,
              placeholder: 'Search tickets',
              ajax: {
                url: urlFor('index', {
                  scope_ns: 'o',
                  scope_id: org_name,
                  resource: 'items',
                  root: true
                }),
                dataType: 'json',
                data: function (params) {
                  return {
                    search: params.term
                  };
                },
                processResults: function (data) {
                  return {
                    results: data.result.items
                  };
                }
              },
              escapeMarkup: function (markup) { return markup; },
              templateResult: function (item) {
                return '<p>' + item.title + '</p>';
              },
              templateSelection: function (item) {
                return item.title;
              }
            });
          }
        },
        showNewPolicyForm: function (event) {
          discountPolicyComponent.set({
            'showAddPolicyForm': DEFAULT.showForm,
            'newDiscountPolicy.is_price_based': DEFAULT.priceBasedDiscount,
            'newDiscountPolicy.discount_type': DEFAULT.couponBasedDiscount
          });
          discountPolicyComponent.addFormFields(discountPolicyComponent.get('newDiscountPolicy.is_price_based'));
        },
        onPolicyChange: function (event) {
          discountPolicyComponent.set('newDiscountPolicy.is_price_based', parseInt(event.node.value, 10));
          discountPolicyComponent.addFormFields(discountPolicyComponent.get('newDiscountPolicy.is_price_based'));
        },
        onPolicyTypeChange: function (event) {
          discountPolicyComponent.set('newDiscountPolicy.discount_type', event.node.value);
        },
        addNewPolicy: function (event) {
          let formName = 'adding-new-policy-form';

          let formValidator = new FormValidator(formName, discountPolicyComponent.get('formValidationConfig'), function (errors, event) {
            event.preventDefault();
            discountPolicyComponent.set('newDiscountPolicy.errormsg', DEFAULT.empty);
            if (errors.length > 0) {
              discountPolicyComponent.set('newDiscountPolicy.errormsg.' + errors[0].name, errors[0].message);
            } else {

              discountPolicyComponent.set({
                'newDiscountPolicy.errorMsg': DEFAULT.empty,
                'newDiscountPolicy.creatingPolicy': DEFAULT.showLoader
              });
              let formSelector = '#new-policy-form';
              post({
                url: urlFor('new', {
                  scope_ns: 'o',
                  scope_id: org_name,
                  resource: 'discount_policy',
                  root: true
                }),
                data: getFormParameters(formSelector)
              }).done((remoteData) => {
                discountPolicyComponent.set({
                  'discountPolicies': [remoteData.result.discount_policy],
                  'searchText': discountPolicyComponent.get('newDiscountPolicy.title'),
                  'newDiscountPolicy.creatingPolicy': DEFAULT.hideLoader,
                  'newDiscountPolicy': DEFAULT.empty
                });
                discountPolicyComponent.hideNewPolicyForm();
              }).fail(function (response) {
                let errorMsg = DEFAULT.empty;
                if (response.readyState === 4) {
                  if (response.status === 500) {
                    errorMsg = "Internal Server Error";
                  } else {
                    let errorDescription = response.responseJSON.message;
                    for (let error in errorDescription) {
                      errorMsg += "<p>" + errorDescription[error] + "</p>";
                    }
                  }
                } else {
                  errorMsg = "Unable to connect. Please try again.";
                }
                discountPolicyComponent.set({
                  'newDiscountPolicy.creatingPolicy': DEFAULT.hideLoader,
                  'newDiscountPolicy.errorMsg': errorMsg
                });
              });
            }
          });

          formValidator.setMessage('required', 'Please fill out the this field');
          formValidator.setMessage('numeric', 'Please enter a numberic value');
        },
        hideNewPolicyForm: function (event) {
          discountPolicyComponent.set('showAddPolicyForm', DEFAULT.hideForm);
        },
        showEditPolicyForm: function (event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.showPolicyForm', DEFAULT.showForm);
          discountPolicyComponent.set(discountPolicy +  '.errormsg', DEFAULT.empty);
          discountPolicyComponent.addFormFields(discountPolicyComponent.get(discountPolicy + '.is_price_based'), discountPolicy);
        },
        editPolicy: function (event) {
          let discountPolicy = event.keypath,
            dpId = event.context.id,
            policyFormName = 'edit-policy-form-' + dpId;

          let formValidator = new FormValidator(policyFormName, discountPolicyComponent.get('formValidationConfig'), function (errors, event) {
            event.preventDefault();
            discountPolicyComponent.set(discountPolicy + '.errormsg', DEFAULT.empty);
            if (errors.length > 0) {
              discountPolicyComponent.set(discountPolicy + '.errormsg.'+ errors[0].name, errors[0].message);
            } else {
              discountPolicyComponent.set(discountPolicy + '.editingPolicy', DEFAULT.showLoader);
              let formSelector = '#policy-form-' + dpId;

              post({
                url: urlFor('edit', {
                  scope_ns: 'o',
                  scope_id: org_name,
                  resource: 'discount_policy',
                  id: dpId,
                  root: true
                }),
                data: getFormParameters(formSelector)
              }).done((remoteData) => {
                discountPolicyComponent.set(discountPolicy + '.editingPolicy', DEFAULT.hideLoader);
                discountPolicyComponent.set(discountPolicy, remoteData.result.discount_policy);
                discountPolicyComponent.set(discountPolicy + '.showPolicyForm', DEFAULT.hideForm);
                scrollToElement('#dp-' + dpId);
              }).fail(function (response) {
                let errorMsg = DEFAULT.empty;
                if (response.readyState === 4) {
                  if (response.status === 500) {
                    errorMsg = "Internal Server Error"
                  } else {
                    let errorDescription = response.responseJSON.message;
                    for (let error in errorDescription) {
                      errorMsg += '<p>' + errorDescription[error] + '</p>';
                    }
                  }
                } else {
                  errorMsg = "Unable to connect. Please try again."
                }
                discountPolicyComponent.set(discountPolicy + '.editingPolicy', DEFAULT.hideLoader);
                discountPolicyComponent.set(discountPolicy + '.errorMsg', errorMsg);
              });
            }
          });

          formValidator.setMessage('required', 'Please fill out the this field');
          formValidator.setMessage('numeric', 'Please enter a numberic value');

        },
        hideEditPolicyForm: function (event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.showPolicyForm', DEFAULT.hideForm);
        },
        showCouponForm: function (event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.count', DEFAULT.usageCount);
          discountPolicyComponent.set(discountPolicy + '.showCouponForm', DEFAULT.showForm);
        },
        generateCoupon: function (event) {
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

          let formValidator = new FormValidator(couponFormName, validationConfig, function (errors, event) {
            event.preventDefault();
            discountPolicyComponent.set(discountPolicy + '.errormsg', DEFAULT.empty);
            if (errors.length > 0) {
              discountPolicyComponent.set(discountPolicy + '.errormsg.'+ errors[0].name, errors[0].message);
            } else {
              let formSelector = '#new-coupon-' + dpId;
              discountPolicyComponent.set(discountPolicy+ '.generatingCoupon', DEFAULT.showLoader);
              discountPolicyComponent.set(discountPolicy + '.generateCouponErrorMsg', DEFAULT.empty);

              post({
                url: urlFor('new', {
                  scope_ns: 'discount_policy',
                  scope_id: dpId,
                  resource: 'coupons',
                  root: true
                }),
                data: getFormParameters(formSelector)
              }).done((remoteData) => {
                discountPolicyComponent.set(discountPolicy + '.coupons', remoteData.result.coupons);
                discountPolicyComponent.set(discountPolicy + '.generatingCoupon', DEFAULT.hideLoader);
                $('#generated-coupons-' + dpId).modal('show');
                new Clipboard('.copy-coupons');
              }).fail(function (response) {
                let errorMsg = DEFAULT.empty;
                if (response.readyState === 4) {
                  if (response.status === 500) {
                    errorMsg = "Internal Server Error"
                  } else {
                    let errorDescription = response.responseJSON.message;
                    for (let error in errorDescription) {
                      errorMsg += '<p>' + errorDescription[error] + '</p>';
                    }
                  }
                } else {
                  errorMsg = "Unable to connect. Please try again."
                }
                discountPolicyComponent.set(discountPolicy + '.generatingCoupon', DEFAULT.hideLoader);
                discountPolicyComponent.set(discountPolicy + '.generateCouponErrorMsg', errorMsg);
              });
            }
          });
          formValidator.setMessage('required', 'Please fill out the this field');
        },
        hideCouponForm: function (event) {
          let discountPolicy = event.keypath;
          discountPolicyComponent.set(discountPolicy + '.showCouponForm', DEFAULT.hideForm);
        },
        getCouponList: function (event) {
          event.original.preventDefault();
          let discountPolicy = event.keypath;
          let dpId = event.context.id;
          discountPolicyComponent.set(discountPolicy + '.loadingCoupons', DEFAULT.showLoader);
          discountPolicyComponent.set(discountPolicy+ '.loadingCouponErrorMsg', DEFAULT.empty);

          fetch({
            url: urlFor('index', {
              scope_ns: 'discount_policy',
              scope_id: dpId,
              resource: 'coupons',
              root: true
            }),
            contentType: 'application/json'
          }).done((remoteData) => {
            discountPolicyComponent.set(discountPolicy + '.coupons', remoteData.result.coupons);
            discountPolicyComponent.set(discountPolicy + '.loadingCoupons', DEFAULT.hideLoader);
            $('#list-coupons-' + dpId).modal('show');
            $('#coupons-list-' + dpId).footable();
            new Clipboard('.copy-coupons-list');
          }).fail(function (response) {
            let errorMsg = DEFAULT.empty;
            if (response.readyState === 4) {
              errorMsg = "Internal Server Error"
            } else {
              errorMsg = "Unable to connect. Please try again."
            }
            discountPolicyComponent.set(discountPolicy + '.loadingCoupons', DEFAULT.hideLoader);
            discountPolicyComponent.set(discountPolicy + '.loadingCouponErrorMsg', errorMsg);
          });

        },
        oncomplete: function () {

          discountPolicyComponent.observe('searchText', function (searchText, prevSearchText) {
            if (searchText.length > 2) {
              discountPolicyComponent.refresh(searchText);
            } else if (searchText.length === 0 && prevSearchText) {
              discountPolicyComponent.refresh();
            }
          });

          discountPolicyComponent.set('pages', _.range(1, discountPolicyComponent.get('totalPages') + 1));

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
