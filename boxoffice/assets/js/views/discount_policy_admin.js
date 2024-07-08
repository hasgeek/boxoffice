/* eslint-disable no-unused-vars */
import {
  Util,
  fetch,
  post,
  scrollToElement,
  getFormParameters,
  getCsrfToken,
  updateBrowserHistory,
  urlFor,
  setPageTitle,
} from '../models/util';
import { DiscountPolicyTemplate } from '../templates/admin_discount_policy.html';
import { SideBarView } from './sidebar';

const NProgress = require('nprogress');
const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');
const _ = require('underscore');
const Clipboard = require('clipboard');
const FormValidator = require('validate-js');
const rome = require('rome');

export const DiscountPolicyView = {
  render({ accountName, search, page, size } = {}) {
    let url;
    if (search) {
      url = urlFor('search', {
        scope_ns: 'o',
        scope_id: accountName,
        resource: 'discount_policy',
        root: true,
        search,
        page,
        size,
      });
    } else {
      url = urlFor('index', {
        scope_ns: 'o',
        scope_id: accountName,
        resource: 'discount_policy',
        root: true,
        page,
        size,
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
      empty: '',
    };

    fetch({
      url,
    }).done(
      ({
        account_title: accountTitle,
        discount_policies: discountPolicies,
        currency_symbol: currencySymbol,
        total_pages: totalPages,
        paginated,
        current_page: currentPage,
      }) => {
        // Initial render
        const discountPolicyComponent = new Ractive({
          el: '#main-content-area',
          template: DiscountPolicyTemplate,
          transitions: { fly },
          data: {
            accountName,
            accountTitle,
            discountPolicies,
            currencySymbol,
            paginated,
            totalPages,
            currentPage,
            size: 20,
            showAddPolicyForm: false,
            newDiscountPolicy: '',
            searchText: search,
            eventUrl: '',
            formValidationConfig: [
              {
                name: 'title',
                rules: 'required|max_length[250]',
              },
              {
                name: 'is_price_based',
                rules: 'required',
              },
              {
                name: 'discount_type',
                rules: 'required',
              },
              {
                name: 'discount_code_base',
                rules: 'required|max_length[20]',
              },
              {
                name: 'bulk_coupon_usage_limit',
                rules: 'required|numeric',
              },
              {
                name: 'item_quantity_min',
                rules: 'required|numeric',
              },
              {
                name: 'amount',
                rules: 'required|numeric',
              },
              {
                name: 'start_at',
                rules: 'required',
              },
              {
                name: 'end_at',
                rules: 'required',
              },
              {
                name: 'percentage',
                rules: 'required|numeric',
              },
              {
                name: 'tickets',
                rules: 'required',
              },
            ],
            getDiscountedItems(dpItems) {
              return dpItems.map((ticket) => ticket.id).join(',');
            },
            getCsrfToken() {
              // Defined as a function so that it is called every time the form is opened
              return getCsrfToken();
            },
            formatToIndianRupee(amount) {
              return Util.formatToIndianRupee(amount);
            },
          },
          refresh(refreshSearch = '', refreshPage = '', refreshPageSize = '') {
            let refreshUrl;
            if (refreshSearch) {
              refreshUrl = urlFor('search', {
                scope_ns: 'o',
                scope_id: accountName,
                resource: 'discount_policy',
                root: true,
                search: refreshSearch,
                page: refreshPage,
                size: refreshPageSize || discountPolicyComponent.get('size'),
              });
            } else {
              refreshUrl = urlFor('index', {
                scope_ns: 'o',
                scope_id: accountName,
                resource: 'discount_policy',
                root: true,
                page: refreshPage,
                size: refreshPageSize || discountPolicyComponent.get('size'),
              });
            }

            NProgress.start();
            fetch({
              url: refreshUrl,
            }).done((remoteData) => {
              discountPolicyComponent.set({
                discountPolicies: remoteData.discount_policies,
                paginated: remoteData.paginated,
                totalPages: remoteData.total_pages,
                currentPage: remoteData.current_page,
                pages: _.range(1, remoteData.total_pages + 1),
              });
              NProgress.done();
              updateBrowserHistory(refreshUrl);
            });
            scrollToElement(`#${discountPolicyComponent.el.id}`);
          },
          paginate(event, givenPage) {
            event.original.preventDefault();
            discountPolicyComponent.refresh(this.get('searchText'), givenPage, size);
          },
          clearSearchField() {
            discountPolicyComponent.set('searchText', DEFAULT.empty);
          },
          addFormFields(isPriceBased, discountPolicy) {
            if (isPriceBased) {
              let addItemSelector;
              let startDateSelector;
              let endDateSelector;

              if (discountPolicy) {
                const discountPolicyId = discountPolicyComponent.get(
                  `${discountPolicy}.id`
                );
                addItemSelector = `#add-item-${discountPolicyId}`;
                startDateSelector = `start-date-${discountPolicyId}`;
                endDateSelector = `end-date-${discountPolicyId}`;
              } else {
                addItemSelector = '#add-item';
                startDateSelector = 'start-date';
                endDateSelector = 'end-date';
              }

              $(addItemSelector).select2({
                minimumInputLength: 3,
                placeholder: {
                  id: '-1',
                  title: 'Search tickets',
                },
                ajax: {
                  url: urlFor('index', {
                    scope_ns: 'o',
                    scope_id: accountName,
                    resource: 'tickets',
                    root: true,
                  }),
                  dataType: 'json',
                  data(params) {
                    return {
                      search: params.term,
                    };
                  },
                  processResults(data) {
                    return {
                      results: data.result.tickets,
                    };
                  },
                },
                // Do not want to escape markup since html is displayed in the results
                escapeMarkup(markup) {
                  return markup;
                },
                templateResult(ticket) {
                  return `<p>${ticket.title}</p>`;
                },
                templateSelection(ticket) {
                  return ticket.title;
                },
              });

              rome(document.getElementById(startDateSelector));
              rome(document.getElementById(endDateSelector));
            } else {
              let addItemsSelector;

              if (discountPolicy) {
                const dpId = discountPolicyComponent.get(`${discountPolicy}.id`);
                addItemsSelector = `#add-items-${dpId}`;
              } else {
                addItemsSelector = '#add-items';
              }

              $(addItemsSelector).select2({
                minimumInputLength: 3,
                multiple: true,
                placeholder: 'Search tickets',
                ajax: {
                  url: urlFor('index', {
                    scope_ns: 'o',
                    scope_id: accountName,
                    resource: 'tickets',
                    root: true,
                  }),
                  dataType: 'json',
                  data(params) {
                    return {
                      search: params.term,
                    };
                  },
                  processResults(data) {
                    return {
                      results: data.result.tickets,
                    };
                  },
                },
                escapeMarkup(markup) {
                  return markup;
                },
                templateResult(ticket) {
                  return `<p>${ticket.title}</p>`;
                },
                templateSelection(ticket) {
                  return ticket.title;
                },
              });
            }
          },
          showNewPolicyForm(event) {
            discountPolicyComponent.set({
              showAddPolicyForm: DEFAULT.showForm,
              'newDiscountPolicy.is_price_based': DEFAULT.priceBasedDiscount,
              'newDiscountPolicy.discount_type': DEFAULT.couponBasedDiscount,
            });
            discountPolicyComponent.addFormFields(
              discountPolicyComponent.get('newDiscountPolicy.is_price_based')
            );
          },
          onPolicyChange(event) {
            discountPolicyComponent.set(
              'newDiscountPolicy.is_price_based',
              parseInt(event.node.value, 10)
            );
            discountPolicyComponent.addFormFields(
              discountPolicyComponent.get('newDiscountPolicy.is_price_based')
            );
          },
          onPolicyTypeChange(event) {
            discountPolicyComponent.set(
              'newDiscountPolicy.discount_type',
              event.node.value
            );
          },
          addNewPolicy(event) {
            const formName = 'adding-new-policy-form';

            const formValidator = new FormValidator(
              formName,
              discountPolicyComponent.get('formValidationConfig'),
              (errors, e) => {
                e.preventDefault();
                discountPolicyComponent.set(
                  'newDiscountPolicy.errormsg',
                  DEFAULT.empty
                );
                if (errors.length > 0) {
                  discountPolicyComponent.set(
                    `newDiscountPolicy.errormsg.${errors[0].name}`,
                    errors[0].message
                  );
                } else {
                  discountPolicyComponent.set({
                    'newDiscountPolicy.errorMsg': DEFAULT.empty,
                    'newDiscountPolicy.creatingPolicy': DEFAULT.showLoader,
                  });
                  const formSelector = '#new-policy-form';
                  post({
                    url: urlFor('new', {
                      scope_ns: 'o',
                      scope_id: accountName,
                      resource: 'discount_policy',
                      root: true,
                    }),
                    data: getFormParameters(formSelector),
                  })
                    .done((remoteData) => {
                      discountPolicyComponent.set({
                        discountPolicies: [remoteData.result.discount_policy],
                        searchText: discountPolicyComponent.get(
                          'newDiscountPolicy.title'
                        ),
                        'newDiscountPolicy.creatingPolicy': DEFAULT.hideLoader,
                        newDiscountPolicy: DEFAULT.empty,
                      });
                      discountPolicyComponent.hideNewPolicyForm();
                    })
                    .fail((response) => {
                      let errorMsg = DEFAULT.empty;
                      if (response.readyState === 4) {
                        if (response.status === 500) {
                          errorMsg = 'Internal Server Error';
                        } else {
                          const errorDescription = response.responseJSON.errors;
                          errorDescription.forEach((error) => {
                            errorMsg += `<p>${errorDescription[error]}</p>`;
                          });
                        }
                      } else {
                        errorMsg = 'Unable to connect. Please try again.';
                      }
                      discountPolicyComponent.set({
                        'newDiscountPolicy.creatingPolicy': DEFAULT.hideLoader,
                        'newDiscountPolicy.errorMsg': errorMsg,
                      });
                    });
                }
              }
            );

            formValidator.setMessage('required', 'Please fill out this field');
            formValidator.setMessage('numeric', 'Please enter a numeric value');
          },
          hideNewPolicyForm(event) {
            discountPolicyComponent.set('showAddPolicyForm', DEFAULT.hideForm);
          },
          showEditPolicyForm(event) {
            const discountPolicy = event.keypath;
            discountPolicyComponent.set(
              `${discountPolicy}.showPolicyForm`,
              DEFAULT.showForm
            );
            discountPolicyComponent.set(`${discountPolicy}.errormsg`, DEFAULT.empty);
            discountPolicyComponent.addFormFields(
              discountPolicyComponent.get(`${discountPolicy}.is_price_based`),
              discountPolicy
            );
          },
          editPolicy(event) {
            const discountPolicy = event.keypath;
            const dpId = event.context.id;
            const policyFormName = `edit-policy-form-${dpId}`;

            const formValidator = new FormValidator(
              policyFormName,
              discountPolicyComponent.get('formValidationConfig'),
              (errors, e) => {
                e.preventDefault();
                discountPolicyComponent.set(
                  `${discountPolicy}.errormsg`,
                  DEFAULT.empty
                );
                if (errors.length > 0) {
                  discountPolicyComponent.set(
                    `${discountPolicy}.errormsg.${errors[0].name}`,
                    errors[0].message
                  );
                } else {
                  discountPolicyComponent.set(
                    `${discountPolicy}.editingPolicy`,
                    DEFAULT.showLoader
                  );
                  const formSelector = `#policy-form-${dpId}`;

                  post({
                    url: urlFor('edit', {
                      resource: 'discount_policy',
                      id: dpId,
                      root: true,
                    }),
                    data: getFormParameters(formSelector),
                  })
                    .done((remoteData) => {
                      discountPolicyComponent.set(
                        `${discountPolicy}.editingPolicy`,
                        DEFAULT.hideLoader
                      );
                      discountPolicyComponent.set(
                        discountPolicy,
                        remoteData.result.discount_policy
                      );
                      discountPolicyComponent.set(
                        `${discountPolicy}.showPolicyForm`,
                        DEFAULT.hideForm
                      );
                      scrollToElement(`#dp-${dpId}`);
                    })
                    .fail((response) => {
                      let errorMsg = DEFAULT.empty;
                      if (response.readyState === 4) {
                        if (response.status === 500) {
                          errorMsg = 'Internal Server Error';
                        } else {
                          const errorDescription = response.responseJSON.errors;
                          errorDescription.forEach((error) => {
                            errorMsg += `<p>${errorDescription[error]}</p>`;
                          });
                        }
                      } else {
                        errorMsg = 'Unable to connect. Please try again.';
                      }
                      discountPolicyComponent.set(
                        `${discountPolicy}.editingPolicy`,
                        DEFAULT.hideLoader
                      );
                      discountPolicyComponent.set(
                        `${discountPolicy}.errorMsg`,
                        errorMsg
                      );
                    });
                }
              }
            );

            formValidator.setMessage('required', 'Please fill out this field');
            formValidator.setMessage('numeric', 'Please enter a numeric value');
          },
          hideEditPolicyForm(event) {
            const discountPolicy = event.keypath;
            discountPolicyComponent.set(
              `${discountPolicy}.showPolicyForm`,
              DEFAULT.hideForm
            );
          },
          showCouponForm(event) {
            const discountPolicy = event.keypath;
            discountPolicyComponent.set(`${discountPolicy}.count`, DEFAULT.usageCount);
            discountPolicyComponent.set(
              `${discountPolicy}.showCouponForm`,
              DEFAULT.showForm
            );
          },
          generateCoupon(event) {
            const discountPolicy = event.keypath;
            const dpId = event.context.id;
            const validationConfig = [
              {
                name: 'count',
                rules: 'required|numeric',
              },
              {
                name: 'usage_limit',
                rules: 'required|numeric',
              },
            ];
            const couponFormName = `generate-coupon-form-${dpId}`;

            const formValidator = new FormValidator(
              couponFormName,
              validationConfig,
              (errors, e) => {
                e.preventDefault();
                discountPolicyComponent.set(
                  `${discountPolicy}.errormsg`,
                  DEFAULT.empty
                );
                if (errors.length > 0) {
                  discountPolicyComponent.set(
                    `${discountPolicy}.errormsg.${errors[0].name}`,
                    errors[0].message
                  );
                } else {
                  const formSelector = `#new-coupon-${dpId}`;
                  discountPolicyComponent.set(
                    `${discountPolicy}.generatingCoupon`,
                    DEFAULT.showLoader
                  );
                  discountPolicyComponent.set(
                    `${discountPolicy}.generateCouponErrorMsg`,
                    DEFAULT.empty
                  );

                  post({
                    url: urlFor('new', {
                      scope_ns: 'discount_policy',
                      scope_id: dpId,
                      resource: 'coupons',
                      root: true,
                    }),
                    data: getFormParameters(formSelector),
                  })
                    .done((remoteData) => {
                      discountPolicyComponent.set(
                        `${discountPolicy}.coupons`,
                        remoteData.result.coupons
                      );
                      discountPolicyComponent.set(
                        `${discountPolicy}.generatingCoupon`,
                        DEFAULT.hideLoader
                      );
                      discountPolicyComponent.set('eventUrl', DEFAULT.empty);
                      $(`#generated-coupons-${dpId}`).modal('show');
                      const clipboard = new Clipboard('.copy-coupons');
                      clipboard.destroy();
                    })
                    .fail((response) => {
                      let errorMsg = DEFAULT.empty;
                      if (response.readyState === 4) {
                        if (response.status === 500) {
                          errorMsg = 'Internal Server Error';
                        } else {
                          const errorDescription = response.responseJSON.errors;
                          errorDescription.forEach((error) => {
                            errorMsg += `<p>${errorDescription[error]}</p>`;
                          });
                        }
                      } else {
                        errorMsg = 'Unable to connect. Please try again.';
                      }
                      discountPolicyComponent.set(
                        `${discountPolicy}.generatingCoupon`,
                        DEFAULT.hideLoader
                      );
                      discountPolicyComponent.set(
                        `${discountPolicy}.generateCouponErrorMsg`,
                        errorMsg
                      );
                    });
                }
              }
            );
            formValidator.setMessage('required', 'Please fill out this field');
          },
          hideCouponForm(event) {
            const discountPolicy = event.keypath;
            discountPolicyComponent.set(
              `${discountPolicy}.showCouponForm`,
              DEFAULT.hideForm
            );
          },
          getCouponList(event) {
            event.original.preventDefault();
            const discountPolicy = event.keypath;
            const dpId = event.context.id;
            discountPolicyComponent.set(
              `${discountPolicy}.loadingCoupons`,
              DEFAULT.showLoader
            );
            discountPolicyComponent.set(
              `${discountPolicy}.loadingCouponErrorMsg`,
              DEFAULT.empty
            );

            fetch({
              url: urlFor('index', {
                scope_ns: 'discount_policy',
                scope_id: dpId,
                resource: 'coupons',
                root: true,
              }),
              contentType: 'application/json',
            })
              .done((remoteData) => {
                discountPolicyComponent.set(
                  `${discountPolicy}.coupons`,
                  remoteData.result.coupons
                );
                discountPolicyComponent.set(
                  `${discountPolicy}.loadingCoupons`,
                  DEFAULT.hideLoader
                );
                $(`#list-coupons-${dpId}`).modal('show');
                $(`#coupons-list-${dpId}`).footable();
                const clipboard = new Clipboard('.copy-coupons-list');
                clipboard.destroy();
              })
              .fail((response) => {
                let errorMsg = DEFAULT.empty;
                if (response.readyState === 4) {
                  errorMsg = 'Internal Server Error';
                } else {
                  errorMsg = 'Unable to connect. Please try again.';
                }
                discountPolicyComponent.set(
                  `${discountPolicy}.loadingCoupons`,
                  DEFAULT.hideLoader
                );
                discountPolicyComponent.set(
                  `${discountPolicy}.loadingCouponErrorMsg`,
                  errorMsg
                );
              });
          },
          oncomplete() {
            let searchTimeout;
            let lastRegisteredSearch = '';
            discountPolicyComponent.observe(
              'searchText',
              (searchText, prevSearchText) => {
                if (searchText !== lastRegisteredSearch) {
                  if (searchText.length > 2) {
                    window.clearTimeout(searchTimeout);
                    lastRegisteredSearch = searchText;
                    searchTimeout = window.setTimeout(() => {
                      discountPolicyComponent.refresh(searchText);
                    }, 1000);
                  } else if (searchText.length === 0) {
                    discountPolicyComponent.refresh();
                  }
                }
              }
            );
            discountPolicyComponent.set(
              'pages',
              _.range(1, discountPolicyComponent.get('totalPages') + 1)
            );
          },
        });

        SideBarView.render('discount-policies', {
          accountName,
          accountTitle,
        });
        setPageTitle('Discount policies', accountTitle);
        NProgress.done();

        window.addEventListener('popstate', (event) => {
          NProgress.configure({ showSpinner: false }).start();
        });
      }
    );
  },
};

export { DiscountPolicyView as default };
