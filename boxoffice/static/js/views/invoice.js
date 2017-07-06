window.Boxoffice = window.Boxoffice || {};

window.Boxoffice.Invoice = {
  config: {
    baseURL: window.location.origin,
    submit: {
      method: 'POST',
      urlFor: function(id) {
        return Boxoffice.Invoice.config.baseURL + '/order/' + id + '/invoice';
      }
    }
  },
  init: function(invoiceDetails) {
    var invoice = this;
    invoice.formComponent = new Ractive({
      el: '#boxoffice-invoice',
      template: '#boxoffice-invoice-form-template',
      data: {
        invoiceDetails: invoiceDetails,
        editDetails: true,
        errorMsg: ""
      },
      scrollTop: function() {
        $('html,body').animate({ scrollTop: $(invoiceComponent.el).offset().top }, '300');
      },
      submitInvoiceDetails: function(event) {
        var validationConfig = [{
          name: 'taxid',
          rules: 'max_length[255]'
        },
        {
          name: 'invoicee_name',
          rules: 'required|max_length[255]'
        },
        {
          name: 'street_address',
          rules: 'required|max_length[255]'
        },
        {
          name: 'city',
          rules: 'required|max_length[255]'
        },
        {
          name: 'state',
          rules: 'required|max_length[255]'
        },
        {
          name: 'country',
          rules: 'required|max_length[255]'
        },
        {
          name: 'postcode',
          rules: 'required|max_length[255]'
        }];

        var formValidator = new FormValidator('invoice-details-form', validationConfig, function(errors, event) {
          event.preventDefault();
                    console.log("form submit");
          invoice.formComponent.set('invoiceDetails.errormsg', '');
          if (errors.length > 0) {
            invoice.formComponent.set('invoiceDetails.errormsg.' + errors[0].name, errors[0].message);
            invoice.formComponent.scrollTop();
          } else {
            invoice.formComponent.set('invoiceDetails.submittingInvoiceDetails', true);
            invoice.formComponent.postInvoiceDetails();
          }
        });
      },
      postInvoiceDetails: function() {
        console.log("url", invoice.config.submit.urlFor(invoice.formComponent.get('invoiceDetails.id')));
        console.log("details", invoice.formComponent.get('invoiceDetails.invoicee_name'))
        $.ajax({
          url: invoice.config.submit.urlFor(invoice.formComponent.get('invoiceDetails.id')),
          type: invoice.config.submit.method,
          dataType: 'json',
          contentType: 'application/json',
          data: JSON.stringify({
            invoice:{
              taxid: invoice.formComponent.get('invoiceDetails.taxid'),
              invoicee_name: invoice.formComponent.get('invoiceDetails.invoicee_name'),
              street_address: invoice.formComponent.get('invoiceDetails.street_address'),
              city: invoice.formComponent.get('invoiceDetails.city'),
              state: invoice.formComponent.get('invoiceDetails.state'),
              country: invoice.formComponent.get('invoiceDetails.country'),
              postcode: invoice.formComponent.get('invoiceDetails.postcode')
            }
          }),
          timeout: 5000,
          retries: 5,
          retryInterval: 5000,
          success: function(data) {
            invoice.formComponent.set({
              'invoiceDetails.submittingBuyerAddress': false,
              'editDetails': false,
            });
          },
          error: function(response) {
            var ajaxLoad = this;
            ajaxLoad.retries -= 1;
            var errorMsg;
            if (response.readyState === 4) {
              errorMsg = JSON.parse(response.responseText).message + ". Sorry, something went wrong. Please write to us at support@hasgeek.com.";
              invoice.formComponent.set({
                'errorMsg': errorMsg,
                'invoiceDetails.submittingBuyerAddress': false
              });
            }
            else if (response.readyState === 0) {
              if (ajaxLoad.retries < 0) {
                errorMsg = "Unable to connect. Please write to us at support@hasgeek.com.";
                invoice.formComponent.set({
                  'errorMsg': errorMsg,
                  'invoiceDetails.submittingBuyerAddress': false
                });
              } else {
                setTimeout(function() {
                  $.post(ajaxLoad);
                }, ajaxLoad.retryInterval);
              }
            }
          }
        });
      }
    });
  }
};

