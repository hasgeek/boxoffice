import {xhrRetry, getFormJSObject} from '../models/util.js';
import {InvoiceEditFormTemplate} from '../templates/invoice_edit_form.html.js';

export const Invoice = {
  config: {
    baseURL: window.location.origin,
    view: {
      method: 'GET',
      urlFor: function() {
        return window.location.href;
      }
    },
    submit: {
      method: 'POST',
      urlFor: function(accessToken) {
        return Invoice.config.baseURL + '/order/' + accessToken + '/invoice';
      }
    }
  },
  init: function() {
    $.ajax({
      url: Invoice.config.view.urlFor(),
      type: Invoice.config.view.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success: function(data) {
        Invoice.view(data);
      },
      error: function(response) {
        var ajaxLoad = this;
        var onServerError = function() {
          var errorMsg = "Server error. ";
          $("#error-description").html(errorMsg);
        };
        var onNetworkError = function() {
          var errorMsg = "Unable to connect. Please try again later.";
          $("#notify-msg").html(errorMsg);
        };
        ajaxLoad.retries -= 1;
        xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
      }
    });
  },
  view: function(data) {
    var invoice = this;
    invoice.formComponent = new Ractive({
      el: '#boxoffice-invoice',
      template: InvoiceEditFormTemplate,
      data: {
        invoices: data.invoices,
        accessToken: data.access_token,
        utils : {
          states: data.states,
          countries: data.countries
        }
      },
      scrollTop: function() {
        $('html,body').animate({ scrollTop: $(invoiceComponent.el).offset().top }, '300');
      },
      submitInvoiceDetails: function(event, invoice_item, invoice_id) {
        var validationConfig = [{
          name: 'invoicee_name',
          rules: 'required'
        },
        {
          name: 'invoicee_email',
          rules: 'required|valid_email'
        },
        {
          name: 'street_address',
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

        var invoiceForm = 'invoice-details-form-' + invoice_id;

        var formValidator = new FormValidator(invoiceForm, validationConfig, function(errors, event) {
          event.preventDefault();
          invoice.formComponent.set(invoice_item + '.errormsg', '');
          if (errors.length > 0) {
            invoice.formComponent.set(invoice_item + '.errormsg.' + errors[0].name, errors[0].message);
            invoice.formComponent.scrollTop();
          } else {
            invoice.formComponent.set(invoice_item + '.submittingInvoiceDetails', true);
            invoice.formComponent.postInvoiceDetails(invoice_item, invoice_id);
          }
        });

        formValidator.setMessage('required', 'Please fill out the %s field');
        formValidator.setMessage('valid_email', 'Please enter a valid email');
      },
      postInvoiceDetails: function(invoice_item, invoice_id) {
        var invoiceForm = '#' + 'invoice-' + invoice_id;
        var invoiceDetails = getFormJSObject(invoiceForm);

        $.ajax({
          url: invoice.config.submit.urlFor(invoice.formComponent.get('accessToken')),
          type: invoice.config.submit.method,
          dataType: 'json',
          contentType: 'application/json',
          data: JSON.stringify({
            invoice: invoiceDetails,
            invoice_id: invoice_id
          }),
          timeout: 5000,
          retries: 5,
          retryInterval: 5000,
          success: function(data) {
            invoice.formComponent.set(invoice_item + '.submittingInvoiceDetails', false);
            invoice.formComponent.set(invoice_item + '.hideForm', true);
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
              }
              else {
                errorTxt = "<p>" + JSON.parse(response.responseText).message + "<p>";
              }
              invoice.formComponent.set(invoice_item + '.errorMsg', errorTxt);
              invoice.formComponent.set(invoice_item + '.submittingInvoiceDetails', false);
            };
            var onNetworkError = function() {
              var errorMsg = "<p>Unable to connect. Please write to us at support@hasgeek.com.<p>";
              invoice.formComponent.set(invoice_item + '.errorMsg', errorMsg);
              invoice.formComponent.set(invoice_item + '.submittingInvoiceDetails', false);
            };
            ajaxLoad.retries -= 1;
            xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
          }
        });
      },
      showInvoiceForm: function(event, invoice_item) {
        event.original.preventDefault();
        invoice.formComponent.set(invoice_item + '.hideForm', false);
      }
    });
  }
};

