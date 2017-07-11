window.Boxoffice = window.Boxoffice || {};

window.Boxoffice.Invoice = {
  config: {
    baseURL: window.location.origin,
    submit: {
      method: 'POST',
      urlFor: function(accessToken) {
        return Boxoffice.Invoice.config.baseURL + '/order/' + accessToken + '/invoice';
      }
    }
  },
  init: function(invoices, accessToken, states, countries) {
    var invoice = this;
    invoice.formComponent = new Ractive({
      el: '#boxoffice-invoice',
      template: '#boxoffice-invoice-form-template',
      data: {
        invoices: invoices,
        accessToken: accessToken,
        utils : {
          states: states,
          countries: countries
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
          rules: 'required'
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

        formValidator.setMessage('required', 'Please fill out the this field');
      },
      postInvoiceDetails: function(invoice_item, invoice_id) {
        var invoiceForm = 'invoice-' + invoice_id;
        var formElements = $('#'+ invoiceForm).serializeArray();
        var invoiceDetails ={};
        for (var formIndex=0; formIndex < formElements.length; formIndex++) {
          if (formElements[formIndex].value) {
            invoiceDetails[formElements[formIndex].name] = formElements[formIndex].value;
          }
        }

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
            ajaxLoad.retries -= 1;
            var errorMsg;
            if (response.readyState === 4) {
              errorMsg = JSON.parse(response.responseText).message + ". Sorry, something went wrong. Please write to us at support@hasgeek.com.";
              invoice.formComponent.set(invoice_item + '.errorMsg', errorMsg);
              invoice.formComponent.set(invoice_item + '.submittingInvoiceDetails', false);
            }
            else if (response.readyState === 0) {
              if (ajaxLoad.retries < 0) {
                errorMsg = "Unable to connect. Please write to us at support@hasgeek.com.";
                invoice.formComponent.set(invoice_item + '.errorMsg', errorMsg);
                invoice.formComponent.set(invoice_item + '.submittingInvoiceDetails', false);
              } else {
                setTimeout(function() {
                  $.post(ajaxLoad);
                }, ajaxLoad.retryInterval);
              }
            }
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

