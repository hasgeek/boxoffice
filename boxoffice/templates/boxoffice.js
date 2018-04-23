window.Boxoffice = {
  // Initial config setup
  config:{
    baseURL: "{{ base_url }}",
    razorpayKeyId: "{{ razorpay_key_id }}",
    orgName: 'HasGeek',
    razorpayBanner: "https://hasgeek.com/static/img/hg-banner.png",
    states: {{ states | tojson }},
    countries: {{ countries | tojson }}
  }
};

{% include "ractive.js" %}

{% raw %}

$(function() {
  Ractive.DEBUG = false;

  var boxoffice = window.Boxoffice;
  boxoffice.util = {};

  var boxoffice = {};
  boxoffice.util = {};
  boxoffice.config = window.Boxoffice.config;

  boxoffice.util.getQueryParams = function() {
    // Returns an array of query parameters
    // Eg: "?code=xxx&cody=yyy" -> ["code=xxx", "code=yyy"]

    // Use the parent window's URL if executed in an iframe, else use the current window's URL
    var searchStr = (window.location !== window.parent.location ? document.referrer : window.location.search).split('?');
    if (searchStr.length > 1) {
      return searchStr[1].split('&');
    }
    return [];
  };

  boxoffice.util.getDiscountCodes = function() {
    // Returns an array of codes used
    //Eg: "?code=xxx&cody=yyy" -> ["xxx", "yyy"]
    return boxoffice.util.getQueryParams().map(function(param){
      var paramSplit = param.split('=');
      if (paramSplit[0] === 'code') {
        return paramSplit[1];
      }
    }).filter(function(val){
      return typeof val !== 'undefined' && val !== "";
    });
  };

  boxoffice.util.getUtmHeaders = function(param){
    /*
    Checks for utm_* headers and returns a hash with the headers set to values.
    If a header occurs more than once, the values are joined to form a single comma-separated string
    */
    var utm_headers = ['utm_campaign', 'utm_source', 'utm_medium', 'utm_id', 'utm_content', 'utm_term', 'gclid'];
    var query_params = boxoffice.util.getQueryParams();
    var utm_values = {};
    var param;
    query_params.forEach(function(query_param){
      param = query_param.split('=')[0];
      if (utm_headers.indexOf(param) > -1) {
        if (!(param in utm_values)) {
          // initialize the utm header
          utm_values[param] = query_param.split('=')[1];
        } else {
          // append the value to form a comma-separated string
          utm_values[param] += ',' + query_param.split('=')[1];
        }
      }
    });
    utm_values['referrer'] = document.referrer;
    return utm_values;
  };

  boxoffice.util.formatDateTime = function(valid_upto) {
    // Returns date in the format 00:00:00 AM, Sun Apr 10 2016
    var date = new Date(valid_upto);
    return date.toLocaleTimeString(['en-US'], {hour: '2-digit', minute: '2-digit'}) + ", " + date.toDateString();
  };

  boxoffice.util.formatDate = function(valid_upto) {
    // Returns date in the format Apr 10 2016
    var date = new Date(valid_upto);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  boxoffice.initResources = function(config) {
    this.config.resources = {
      itemCollection: {
        method: 'GET',
        urlFor: function(){
          return boxoffice.config.baseURL + '/ic/' + config.ic;
        }
      },
      kharcha: {
        method: 'POST',
        urlFor: function(){
          return boxoffice.config.baseURL + '/order/kharcha';
        }
      },
      purchaseOrder: {
        method: 'POST',
        urlFor: function(){
          return boxoffice.config.baseURL + '/ic/' + config.ic + '/order';
        }
      },
      payment: {
        method: 'POST',
        urlFor: function(id){
          return boxoffice.config.baseURL + '/order/' + id + '/payment';
        }
      },
      free: {
        method: 'POST',
        urlFor: function(id){
          return boxoffice.config.baseURL + '/order/' + id + '/free';
        }
      },
      receipt: {
        urlFor: function(accessToken){
          return boxoffice.config.baseURL + "/order/" + accessToken + "/receipt";
        }
      },
      attendeeAssignment: {
        urlFor: function(accessToken){
          return boxoffice.config.baseURL + "/order/" + accessToken + "/ticket";
        }
      },
      invoiceDetails: {
      	method: 'POST',
        urlFor: function(accessToken){
          return boxoffice.config.baseURL + "/order/" + accessToken + "/invoice";
        }
      }
    };
  };

  boxoffice.init = function(widgetConfig) {
    widgetConfig.categories = widgetConfig.categories || [];
    // Config variables provided by the client embedding the widget
    this.widgetConfig = widgetConfig;
    this.initResources({
      ic: widgetConfig.itemCollection
    });

    $.ajax({
      url: boxoffice.config.resources.itemCollection.urlFor(),
      crossDomain: true,
      headers: {'X-Requested-With': 'XMLHttpRequest'},
      dataType: 'json'
    }).done(function(data) {
      var lineItems = [];
      var item_map = {};
      var categories = data.categories;

      /* load inventory from server, initialize lineItems with
      their quantities set to 0 */
      data.categories.forEach(function(category) {
        category.items.forEach(function(item) {
          item_map[item.id] = item;
          lineItems.push({
            'item_id': item.id,
            'item_name': item.name,
            'quantity': 0,
            'item_title': item.title,
            'base_price': item.price,
            'unit_final_amount': undefined,
            'discounted_amount': undefined,
            'final_amount': undefined,
            'item_description': item.description,
            'price_valid_upto': boxoffice.util.formatDate(item.price_valid_upto),
            'has_higher_price': item.has_higher_price,
            'discount_policies': item.discount_policies,
            'quantity_available': item.quantity_available,
            'is_available': item.is_available
          });
        });
      });

      if (widgetConfig.categories.length > 0) {
        categories = widgetConfig.categories.map(function(widget_category) {
          return {
            name: widget_category.name,
            title: widget_category.title,
            items: widget_category.item_ids.map(function(item_id) {
              return item_map[item_id];
            })
          }
        });
      }

      boxoffice.ractive = new Ractive({
        el: '#boxoffice-widget',
        template: data.html,
        data: {
          refund_policy : data.refund_policy,
          order: {
            order_id: '',
            access_token: '',
            line_items: lineItems,
            final_amount: 0.0,
            readyToCheckout: false
          },
          // Prefill name, email, phone if user is found to be logged in
          buyer: {
            fullname: widgetConfig.user_name,
            email: widgetConfig.user_email,
            phone: widgetConfig.user_phone || '+91',
            cashReceiptURL: "",
            attendeeAssignmentURL: ""
          },
          invoice: {
            buyer_taxid: "",
            invoicee_name: "",
            invoicee_company: "",
            invoicee_email: "",
            street_address_1: "",
            street_address_2: "",
            city: "",
            state: "",
            state_code: "KA",
            country_code: "IN",
            postcode: "",
            isFilled: false
          },
          activeTab: 'boxoffice-selectItems',
          tabs: {
            selectItems: {
              id: 'boxoffice-selectItems',
              label: 'Select Tickets',
              complete: false,
              section: {
                categories: categories
              },
              errorMsg: ""
            },
            payment: {
              id: 'boxoffice-payment',
              label: 'Payment',
              complete: false,
              section: {
              },
              errorMsg: ""
            },
            invoice: {
              id: 'boxoffice-invoice',
              label: 'invoice',
              complete: false,
              section: {
              },
              errorMsg: ""
            },
            attendeeDetails: {
              id: 'boxoffice-attendee-details',
              label: 'Attendee details',
              complete: false,
              section: {
              	eventTitle: widgetConfig.paymentDesc,
                eventHashtag: widgetConfig.event_hashtag,
              }
            }
          },
          utils : {
          	states: boxoffice.config.states,
          	countries: boxoffice.config.countries
          }
        },
        scrollTop: function(){
          //Scroll the page up to top of boxoffice widget.
          $('html,body').animate({
            scrollTop: $("#" + boxoffice.ractive.el.id).offset().top
          }, '300');
        },
        selectItems: function(event) {
          // Makes the 'Select Items' tab active
          event.original.preventDefault();
          boxoffice.ractive.calculateOrder();
          boxoffice.ractive.fire('eventAnalytics', 'edit order', 'Edit order', boxoffice.ractive.get('order.final_amount'));
          boxoffice.ractive.set('activeTab', boxoffice.ractive.get('tabs.selectItems.id'));
          boxoffice.ractive.scrollTop();
        },
        xhrRetry: function(ajaxLoad, response, onServerError, onNetworkError) {
          if (response.readyState === 4) {
          	//Server error
            onServerError();
          } else if (response.readyState === 0) {
            if (ajaxLoad.retries < 0) {
              //Network error
              onNetworkError();
            } else {
              setTimeout(function() {
                $.post(ajaxLoad);
              }, ajaxLoad.retryInterval);
            }
          }
        },
        getFormJSObject: function (form) {
          var formElements = $(form).serializeArray();
          var formDetails ={};
          $.each(formElements, function () {
            if (formDetails[this.name] !== undefined) {
              if (!formDetails[this.name].push) {
                formDetails[this.name] = [formDetails[this.name]];
              }
              formDetails[this.name].push(this.value || '');
            } else {
              formDetails[this.name] = this.value || '';
            }
          });
          return formDetails;
        },
        preApplyDiscount: function(discount_coupons) {
          //Ask server for the corresponding line_item for the discount coupon. Add one quantity of that line_item
          $.post({
            url: boxoffice.config.resources.kharcha.urlFor(),
            crossDomain: true,
            dataType: 'json',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            contentType: 'application/json',
            data: JSON.stringify({
              line_items: boxoffice.ractive.get('order.line_items').map(function(line_item) {
                return {
                  quantity: 1,
                  item_id: line_item.item_id
                };
              }),
              discount_coupons: discount_coupons
            }),
            timeout: 5000,
            retries: 5,
            retryInterval: 5000,
            success: function(data) {
              var discount_applicable = false;
              var line_items = boxoffice.ractive.get('order.line_items');
              line_items.forEach(function(line_item) {
                if (data.line_items.hasOwnProperty(line_item.item_id)) {
                  if (data.line_items[line_item.item_id].discounted_amount && line_item.quantity_available > 0) {
                    discount_applicable = true;
                    line_item.unit_final_amount = data.line_items[line_item.item_id].final_amount;
                    line_item.discount_policies.forEach(function(discount_policy){
                      if (data.line_items[line_item.item_id].discount_policy_ids.indexOf(discount_policy.id) >= 0) {
                        discount_policy.pre_applied = true;
                      }
                    });
                  }
                }
              });

              if (discount_applicable) {
                boxoffice.ractive.set('order.line_items',line_items);
                // Scroll to the top of the widget when a discount is pre-applied
                boxoffice.ractive.scrollTop();
              }
            },
            error: function(response) {
            	var ajaxLoad = this;
              ajaxLoad.retries -= 1;
              boxoffice.ractive.xhrRetry(ajaxLoad, response);
            }
          });
        },
        updateOrder: function(event, item_name, quantityAvailable, increment) {
          // Increments or decrements a line item's quantity
          event.original.preventDefault();
          var lineItems = boxoffice.ractive.get('order.line_items');
          lineItems.forEach(function(lineItem) {
            if (lineItem.item_name === item_name) {
              if (increment) {
                if (lineItem.quantity < quantityAvailable) {
                  lineItem.quantity += 1;
                }
                boxoffice.ractive.fire('eventAnalytics', 'add ticket', item_name, lineItem.base_price);
              } else if (lineItem.quantity !== 0) {
                lineItem.quantity -= 1;
                boxoffice.ractive.fire('eventAnalytics', 'remove ticket', item_name, 0);
              }
            }
            if (lineItem.quantity === 0) {
              lineItem.discounted_amount = 0;
              lineItem.final_amount = 0;
              lineItem.discount_policies.forEach(function(discount_policy) {
                discount_policy.activated = false;
              });
            }
          });
          boxoffice.ractive.set({
            'order.line_items': lineItems,
            'tabs.selectItems.errorMsg': '',
            'tabs.selectItems.isLoadingFail': false,
          });
          boxoffice.ractive.calculateOrder();
        },
        calculateOrder: function() {
          // Asks the server for the order's calculation and updates the order
          var lineItems = boxoffice.ractive.get('order.line_items').filter(function(line_item) {
            return line_item.quantity > 0;
          });

          if (lineItems.length) {
            boxoffice.ractive.set('tabs.selectItems' + '.loadingPrice', true);

            $.post({
              url: boxoffice.config.resources.kharcha.urlFor(),
              crossDomain: true,
              dataType: 'json',
              headers: {'X-Requested-With': 'XMLHttpRequest'},
              contentType: 'application/json',
              data: JSON.stringify({
                line_items: lineItems.filter(function(line_item) {
                  return line_item.quantity > 0;
                  }).map(function(line_item) {
                  return {
                    quantity: line_item.quantity,
                    item_id: line_item.item_id
                  };
                }),
                discount_coupons: boxoffice.util.getDiscountCodes()
              }),
              timeout: 5000,
              retries: 5,
              retryInterval: 5000,
              success: function(data) {
                var line_items = boxoffice.ractive.get('order.line_items');
                var readyToCheckout = false;
                line_items.forEach(function(line_item){
                  // TODO: Refactor this to iterate through data.line_items
                  if (data.line_items.hasOwnProperty(line_item.item_id) && line_item.quantity ===  data.line_items[line_item.item_id].quantity) {
                    line_item.final_amount = data.line_items[line_item.item_id].final_amount;
                    line_item.discounted_amount = data.line_items[line_item.item_id].discounted_amount;
                    line_item.quantity_available = data.line_items[line_item.item_id].quantity_available;
                    line_item.is_available = data.line_items[line_item.item_id].is_available;
                    if (!line_item.is_available) {
                      // This item is no longer available, force set the selected quantity to 0.
                      line_item.quantity = 0;
                    }

                    if (!readyToCheckout
                      && data.line_items[line_item.item_id].quantity > 0
                      && data.line_items[line_item.item_id].quantity <= data.line_items[line_item.item_id].quantity_available) {
                      readyToCheckout = true;
                    }

                    line_item.discount_policies.forEach(function(discount_policy){
                      if (data.line_items[line_item.item_id].discount_policy_ids.indexOf(discount_policy.id) >= 0) {
                        discount_policy.activated = true;
                      } else {
                        discount_policy.activated = false;
                      }
                    });
                  }
                });

                if (readyToCheckout) {
                  boxoffice.ractive.set({
                    'order.line_items': line_items,
                    'order.final_amount': data.order.final_amount,
                    'tabs.selectItems.errorMsg': ''
                  });
                }
                boxoffice.ractive.set({
                  'tabs.selectItems.loadingPrice': false,
                  'order.readyToCheckout': readyToCheckout
                });
              },
              error: function(response) {
              	var ajaxLoad = this;
              	var onServerError = function() {
              		boxoffice.ractive.set({
	                  'tabs.selectItems.errorMsg': JSON.parse(response.responseText).message,
	                  'tabs.selectItems.isLoadingFail': true,
	                  'order.readyToCheckout': false
	                });
              	};
              	var onNetworkError = function() {
              		boxoffice.ractive.set({
	                  'tabs.selectItems.errorMsg': "Unable to connect. Please try again later.",
	                  'tabs.selectItems.isLoadingFail': true,
	                  'order.readyToCheckout': false
	                });
              	};
                ajaxLoad.retries -= 1;
              	boxoffice.ractive.xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
              }
            });
          } else {
            boxoffice.ractive.set({
              'order.final_amount': 0,
              'order.readyToCheckout': false
            });
          }
        },
        checkout: function(event) {
          // Transitions the widget to the 'Payment' stage, and initializes
          // the validator.
          event.original.preventDefault();
          boxoffice.ractive.fire('eventAnalytics', 'checkout', 'Checkout', boxoffice.ractive.get('order.final_amount'));
          boxoffice.ractive.set({
            'tabs.payment.errorMsg': '',
            'tabs.selectItems.complete': true,
            'activeTab': boxoffice.ractive.get('tabs.payment.id')
          });
          boxoffice.ractive.scrollTop();

          var validationConfig = [{
            name: 'fullname',
            rules: 'required|max_length[80]'
          },
          {
            name: 'email',
            rules: 'required|valid_email'
          },
          {
            name: 'phone',
            rules: 'required|callback_validate_phone'
          }];

          var formValidator = new FormValidator('buyer-form', validationConfig, function(errors, event) {
            event.preventDefault();
            boxoffice.ractive.set('tabs.payment.errormsg', '');
            if (errors.length > 0) {
              boxoffice.ractive.set('tabs.payment.errormsg.' + errors[0].name, errors[0].message);
              boxoffice.ractive.scrollTop();
            } else {
              boxoffice.ractive.set('tabs.payment.loadingOrder', true);
              boxoffice.ractive.sendOrder();
            }
          });

          formValidator.setMessage('required', 'Please fill out the %s field');
          formValidator.setMessage('valid_email', 'Please enter a valid email');

          formValidator.registerCallback('validate_phone', function(phone) {
            //Remove all punctations (except +) and letters
            phone = phone.replace(/[^0-9+]/g,'');
            boxoffice.ractive.set('buyer.phone', phone);

            var validPhone = /^\+[0-9]+$/;

            if (phone.length > 16) {
              formValidator.setMessage('validate_phone', "Please enter a valid mobile number");
              return false;
            } else if (phone.match(validPhone)) {
              //Indian number starting with '+91'
              if (phone.indexOf('+91') === 0 && phone.length != 13) {
                formValidator.setMessage('validate_phone', "Please enter a valid Indian mobile number");
                return false;
              }
            } else {
              formValidator.setMessage('validate_phone', "Please prefix your phone number with '+' and country code.");
              return false;
            }
          });
        },
        sendOrder: function() {
          boxoffice.ractive.fire('eventAnalytics', 'order creation', 'sendOrder', boxoffice.ractive.get('order.final_amount'));
          var buyerForm = '#boxoffice-buyer-form';
          var buyerDetails = boxoffice.ractive.getFormJSObject(buyerForm);

          $.post({
            url: boxoffice.config.resources.purchaseOrder.urlFor(),
            crossDomain: true,
            dataType: 'json',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            contentType: 'application/json',
            data: JSON.stringify({
              buyer: buyerDetails,
              line_items: boxoffice.ractive.get('order.line_items').filter(function(line_item) {
                return line_item.quantity > 0;
              }).map(function(line_item) {
                return {
                  item_id: line_item.item_id,
                  quantity: line_item.quantity
                };
              }),
              order_session: boxoffice.util.getUtmHeaders(),
              discount_coupons: boxoffice.util.getDiscountCodes()
            }),
            timeout: 5000,
            retries: 5,
            retryInterval: 5000,
            success: function(data) {
              boxoffice.ractive.set({
                'tabs.payment.loadingOrder': false,
                'tabs.payment.errorMsg' : '',
                'order.order_id': data.result.order_id,
                'order.access_token': data.result.order_access_token,
                'order.final_amount': data.result.final_amount
              });
              if (boxoffice.ractive.get('order.final_amount') === 0){
                boxoffice.ractive.completeFreeOrder(data.result.free_order_url);
              } else {
                boxoffice.ractive.capturePayment(data.result.payment_url, data.result.razorpay_payment_id);
              }
              boxoffice.ractive.scrollTop();
            },
            error: function(response) {
              var ajaxLoad = this;
              var onServerError = function() {
                var errorTxt = "";
                var resp = JSON.parse(response.responseText);
                var errors = resp.errors;
                if (errors[0] === 'order calculation error') {
                  boxoffice.ractive.calculateOrder();
                  errorTxt = "<p>" + JSON.parse(response.responseText).message + "<p>";
                } else if (errors && !$.isEmptyObject(errors)) {
                  for (let error in errors) {
                    errorTxt += "<p>" + errors[error] + "</p>"
                  }
                } else {
                  errorTxt = "<p>" + JSON.parse(response.responseText).message + "<p>";
                }
                boxoffice.ractive.set({
	                'tabs.payment.errorMsg': errorTxt,
	                'tabs.payment.loadingOrder': false
	              });
              };
              var onNetworkError = function() {
                var errorTxt = "<p>Unable to connect. Please write to us at support@hasgeek.com.<p>";
                boxoffice.ractive.set({
	                'tabs.payment.errorMsg': errorTxt,
	                'tabs.payment.loadingOrder': false
	              });
              };
              ajaxLoad.retries -= 1;
              boxoffice.ractive.xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
            }
          });
        },
        capturePayment: function(paymentUrl, razorpay_payment_id){
          // Opens the Razorpay widget, on success calls confirmPayment
          boxoffice.ractive.fire('eventAnalytics', 'initiate payment', 'capturePayment', boxoffice.ractive.get('order.final_amount'));
          var razorPayOptions = {
            "key": boxoffice.config.razorpayKeyId,
            //Razorpay expects amount in paisa
            "amount": boxoffice.ractive.get('order.final_amount') * 100,
            "name": boxoffice.widgetConfig.org || boxoffice.config.orgName,
            "description": boxoffice.widgetConfig.paymentDesc,
            "image": boxoffice.widgetConfig.razorpayBanner || boxoffice.config.razorpayBanner,
            // Order id is for razorpay's reference, useful for querying
            "notes": {
              "order_id": boxoffice.ractive.get('order.order_id')
            },
            "handler": function (data) {
              boxoffice.ractive.confirmPayment(paymentUrl, data.razorpay_payment_id);
            },
            "prefill": {
              "name": boxoffice.ractive.get('buyer.fullname'),
              "email": boxoffice.ractive.get('buyer.email'),
              "contact": boxoffice.ractive.get('buyer.phone')
            },
            "theme": {
              "color": "#F37254"
            },
            "modal": {
              "ondismiss": function() {
                boxoffice.ractive.fire('eventAnalytics', 'dismiss payment form', 'razorPay close', boxoffice.ractive.get('order.final_amount'));
              }
            }
          };
          var razorpay = new Razorpay(razorPayOptions);
          razorpay.open();
        },
        confirmPayment: function(paymentUrl, paymentID) {
          // Sends the paymentId to the server, transitions the state to 'Invoice'
          boxoffice.ractive.set('tabs.payment.loadingPaymentConfirmation', true);
          boxoffice.ractive.fire('eventAnalytics', 'capture payment', 'confirmPayment', boxoffice.ractive.get('order.final_amount'));
          $.post({
            url: boxoffice.config.resources.payment.urlFor(boxoffice.ractive.get('order.order_id')),
            crossDomain: true,
            dataType: 'json',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            contentType: 'application/json',
            data: JSON.stringify({pg_paymentid: paymentID}),
            timeout: 60000,
            retries: 5,
            retryInterval: 10000,
            success: function(data) {
              // Set invoice to be the next active tab and pre fill invoice form with buyer's name & email
              boxoffice.ractive.set({
                'tabs.payment.loadingPaymentConfirmation': false,
                'tabs.payment.complete': true,
                'activeTab': boxoffice.ractive.get('tabs.invoice.id'),
                'invoice.invoice_id': data.result.invoice_id,
                'invoice.invoicee_name': boxoffice.ractive.get('buyer.fullname'),
                'invoice.invoicee_email': boxoffice.ractive.get('buyer.email'),
                'buyer.cashReceiptURL': boxoffice.config.resources.receipt.urlFor(boxoffice.ractive.get('order.access_token')),
                'buyer.attendeeAssignmentURL': boxoffice.config.resources.attendeeAssignment.urlFor(boxoffice.ractive.get('order.access_token'))
              });
              boxoffice.ractive.fire('eventAnalytics', 'booking complete', 'confirmPayment success', boxoffice.ractive.get('order.final_amount'));
            },
            error: function(response) {
            	var ajaxLoad = this;
            	var onServerError = function() {
            		boxoffice.ractive.set({
	                'tabs.payment.errorMsg': JSON.parse(response.responseText).message,
	                'tabs.payment.loadingPaymentConfirmation': false
	              });
            	};
            	var onNetworkError = function() {
            		boxoffice.ractive.set({
	                'tabs.payment.errorMsg': "Unable to connect. Please write to us at support@hasgeek.com with your order id " + boxoffice.ractive.get('order.order_id') + ".",
	                'tabs.payment.loadingPaymentConfirmation': false
	              });
            	};
              ajaxLoad.retries -= 1;
              boxoffice.ractive.xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
            }
          });
        },
        completeFreeOrder: function(url) {
          boxoffice.ractive.set('tabs.payment.loadingPaymentConfirmation', true);
          $.post({
            url: boxoffice.config.resources.free.urlFor(boxoffice.ractive.get('order.order_id')),
            crossDomain: true,
            dataType: 'json',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            contentType: 'application/json',
            timeout: 5000,
            retries: 5,
            retryInterval: 5000,
            success: function(data) {
              boxoffice.ractive.set({
                'tabs.payment.loadingPaymentConfirmation': false,
                'tabs.payment.complete': true,
                'tabs.invoice.complete': true,
                'activeTab': boxoffice.ractive.get('tabs.attendeeDetails.id'),
                'buyer.cashReceiptURL': boxoffice.config.resources.receipt.urlFor(boxoffice.ractive.get('order.access_token')),
                'buyer.attendeeAssignmentURL': boxoffice.config.resources.attendeeAssignment.urlFor(boxoffice.ractive.get('order.access_token'))
              });
              boxoffice.ractive.fire('eventAnalytics', 'booking complete', 'completeFreeOrder success', 0);
            },
            error: function(response) {
            	var ajaxLoad = this;
              var onServerError = function() {
								boxoffice.ractive.set({
	                'tabs.payment.errorMsg': JSON.parse(response.responseText).message + ". Sorry, something went wrong. We will get in touch with you shortly. This is your order id " + boxoffice.ractive.get('order.order_id') + ".",
	                'tabs.payment.loadingPaymentConfirmation': false
	              });
              };
              var onNetworkError = function() {
              	boxoffice.ractive.set({
	                'tabs.payment.errorMsg': "Unable to connect. Please write to us at support@hasgeek.com with your order id " + boxoffice.ractive.get('order.order_id') + ".",
	                'tabs.payment.loadingPaymentConfirmation': false
	              });
              };
              ajaxLoad.retries -= 1;
              boxoffice.ractive.xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
            }
          });
        },
        submitInvoiceDetails: function(event) {
          var validationConfig = [{
            name: 'invoicee_name',
            rules: 'required'
          },
          {
            name: 'invoicee_email',
            rules: 'required|valid_email'
          },
          {
            name: 'street_address_1',
            rules: 'required'
          },
          {
            name: 'country_code',
            rules: 'required'
          },
          {
            name: 'state_code',
            rules: 'required'
          },
          {
            name: 'city',
            rules: 'required'
          },
          {
            name: 'postcode',
            rules: 'required'
          }];

          var formValidator = new FormValidator('invoice-details-form', validationConfig, function(errors, event) {
            event.preventDefault();
            boxoffice.ractive.set('invoice.errormsg', '');
            if (errors.length > 0) {
              boxoffice.ractive.set('invoice.errormsg.' + errors[0].name, errors[0].message);
            } else {
              boxoffice.ractive.set('tabs.invoice.submittingInvoiceDetails', true);
              boxoffice.ractive.postInvoiceDetails();
            }
          });

          formValidator.setMessage('required', 'Please fill out this field');
          formValidator.setMessage('valid_email', 'Please enter a valid email');
	      },
	      postInvoiceDetails: function() {
          var invoiceForm = '#boxoffice-invoice-form';
          var invoiceDetails = boxoffice.ractive.getFormJSObject(invoiceForm);

	      	$.post({
            url: boxoffice.config.resources.invoiceDetails.urlFor(boxoffice.ractive.get('order.access_token')),
            crossDomain: true,
            dataType: 'json',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            contentType: 'application/json',
            data: JSON.stringify({
              invoice:invoiceDetails,
              invoice_id: boxoffice.ractive.get('invoice.invoice_id')
            }),
            timeout: 5000,
            retries: 5,
            retryInterval: 5000,
            success: function(data) {
              boxoffice.ractive.set({
                'tabs.invoice.submittingInvoiceDetails': false,
                'tabs.invoice.errorMsg': "",
                'tabs.invoice.complete': true,
                'invoice.isFilled': true,
                'activeTab': boxoffice.ractive.get('tabs.attendeeDetails.id')
              });
              boxoffice.ractive.scrollTop();
              boxoffice.ractive.fire('eventAnalytics', 'submit buyer address', 'sendBuyerAddress success', 0);
            },
            error: function(response) {
            	var ajaxLoad = this;
            	var onServerError = function() {
                var errorTxt = "";
                var errors = JSON.parse(response.responseText).errors;
                if (errors && !$.isEmptyObject(errors)) {
                  for (let error in errors) {
                    errorTxt += "<p>" + errors[error] + "</p>"
                  }
                } else {
                  errorTxt = "<p>" + JSON.parse(response.responseText).message + "<p>";
                }
            		boxoffice.ractive.set({
	                'tabs.invoice.errorMsg': errorTxt,
	                'tabs.invoice.submittingInvoiceDetails': false
	              });
            	};
            	var onNetworkError = function() {
                var errorTxt = "<p>Unable to connect. Please write to us at support@hasgeek.com.<p>";
            		boxoffice.ractive.set({
	                'tabs.invoice.errorMsg': errorTxt,
	                'tabs.invoice.submittingInvoiceDetails': false
	              });
            	};
              ajaxLoad.retries -= 1;
              boxoffice.ractive.xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
            }
          });
	      },
	      proceedToFillAttendeeDetails: function() {
	      	boxoffice.ractive.scrollTop();
	      	boxoffice.ractive.set({
            'tabs.invoice.complete': true,
            'activeTab': boxoffice.ractive.get('tabs.attendeeDetails.id')
          });
	      },
        oncomplete: function() {
          boxoffice.ractive.on('eventAnalytics', function(userAction, label, value) {
            if (typeof boxoffice.ractive.get('sendEventHits') === "undefined") {
              boxoffice.ractive.set('sendEventHits', 0);
              userAction = 'First interaction';
            }
            $(document).trigger('boxofficeTicketingEvents', [userAction, label, value]);
          });

          var discount_coupons = boxoffice.util.getDiscountCodes();
          if (discount_coupons.length) {
            boxoffice.ractive.preApplyDiscount(discount_coupons);
          }
        }
      });
    });
  };

  window.Boxoffice.init = function(widgetConfig) {
	  boxoffice.init(widgetConfig);
  };

  // Raise a custom event once boxoffice.js has been loaded
  if (typeof(window.Event) === "function") {
    var onBoxofficeInit = new Event('onBoxofficeInit');
  } else {
    // 'Event' constructor is not supported by IE
    var onBoxofficeInit = document.createEvent('Event');
    onBoxofficeInit.initEvent('onBoxofficeInit', true, true);
  }
  window.dispatchEvent(onBoxofficeInit);

});
{% endraw %}
