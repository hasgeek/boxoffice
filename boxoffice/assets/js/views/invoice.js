/* eslint-disable no-unused-vars */
import { xhrRetry, getFormJSObject } from '../models/util';
import { InvoiceEditFormTemplate } from '../templates/invoice_edit_form.html';

const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');
const FormValidator = require('validate-js');

export const Invoice = {
  config: {
    baseURL: window.location.origin,
    view: {
      method: 'GET',
      urlFor() {
        return window.location.href;
      },
    },
    submit: {
      method: 'POST',
      urlFor(accessToken) {
        return `${Invoice.config.baseURL}/order/${accessToken}/invoice`;
      },
    },
  },
  init() {
    $.ajax({
      url: Invoice.config.view.urlFor(),
      type: Invoice.config.view.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success(data) {
        Invoice.view(data);
      },
      error(response) {
        const ajaxLoad = this;
        function onServerError() {
          const errorMsg = 'Server error. ';
          $('#error-description').html(errorMsg);
        }
        function onNetworkError() {
          const errorMsg = 'Unable to connect. Please try again later.';
          $('#notify-msg').html(errorMsg);
        }
        ajaxLoad.retries -= 1;
        xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
      },
    });
  },
  view(data) {
    const invoice = this;
    invoice.formComponent = new Ractive({
      el: '#boxoffice-invoice',
      template: InvoiceEditFormTemplate,
      transitions: { fly },
      data: {
        invoices: data.invoices,
        accessToken: data.access_token,
        utils: {
          states: data.states,
          countries: data.countries,
        },
      },
      scrollTop() {
        $('html,body').animate(
          { scrollTop: $(invoice.formComponent.el).offset().top },
          '300'
        );
      },
      submitInvoiceDetails(event, invoiceItem, invoiceId) {
        const validationConfig = [
          {
            name: 'invoicee_name',
            rules: 'required',
          },
          {
            name: 'invoicee_email',
            rules: 'required|valid_email',
          },
          {
            name: 'street_address_1',
            rules: 'required',
          },
          {
            name: 'country_code',
            rules: 'required',
          },
          {
            name: 'state_code',
            rules: 'required',
          },
          {
            name: 'city',
            rules: 'required',
          },
          {
            name: 'postcode',
            rules: 'required',
          },
        ];

        const invoiceForm = `invoice-details-form-${invoiceId}`;

        const formValidator = new FormValidator(
          invoiceForm,
          validationConfig,
          (errors, e) => {
            e.preventDefault();
            invoice.formComponent.set(`${invoiceItem}.errormsg`, '');
            if (errors.length > 0) {
              invoice.formComponent.set(
                `${invoiceItem}.errormsg.${errors[0].name}`,
                errors[0].message
              );
              invoice.formComponent.scrollTop();
            } else {
              invoice.formComponent.set(
                `${invoiceItem}.submittingInvoiceDetails`,
                true
              );
              invoice.formComponent.postInvoiceDetails(invoiceItem, invoiceId);
            }
          }
        );

        formValidator.setMessage('required', 'Please fill out this field');
        formValidator.setMessage('valid_email', 'Please enter a valid email');
      },
      postInvoiceDetails(invoiceItem, invoiceId) {
        const invoiceForm = `#invoice-${invoiceId}`;
        const invoiceDetails = getFormJSObject(invoiceForm);

        $.ajax({
          url: invoice.config.submit.urlFor(invoice.formComponent.get('accessToken')),
          type: invoice.config.submit.method,
          dataType: 'json',
          contentType: 'application/json',
          data: JSON.stringify({
            invoice: invoiceDetails,
            invoice_id: invoiceId,
          }),
          timeout: 5000,
          retries: 5,
          retryInterval: 5000,
          success(successData) {
            invoice.formComponent.set(`${invoiceItem}.errorMsg`, '');
            invoice.formComponent.set(`${invoiceItem}.submittingInvoiceDetails`, false);
            invoice.formComponent.set(`${invoiceItem}.hideForm`, true);
          },
          error(response) {
            const ajaxLoad = this;
            function onServerError() {
              let errorTxt = '';
              const { errors } = JSON.parse(response.responseText);
              if (errors && !$.isEmptyObject(errors)) {
                errors.forEach((error) => {
                  errorTxt += `<p>${errors[error]}</p>`;
                });
              } else {
                errorTxt = `<p>${JSON.parse(response.responseText).message}<p>`;
              }
              invoice.formComponent.set(`${invoiceItem}.errorMsg`, errorTxt);
              invoice.formComponent.set(
                `${invoiceItem}.submittingInvoiceDetails`,
                false
              );
            }
            function onNetworkError() {
              const errorTxt =
                '<p>Unable to connect. Please write to us at support@hasgeek.com.<p>';
              invoice.formComponent.set(`${invoiceItem}.errorMsg`, errorTxt);
              invoice.formComponent.set(
                `${invoiceItem}.submittingInvoiceDetails`,
                false
              );
            }
            ajaxLoad.retries -= 1;
            xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
          },
        });
      },
      showInvoiceForm(event, invoiceItem) {
        event.original.preventDefault();
        invoice.formComponent.set(`${invoiceItem}.hideForm`, false);
      },
    });
  },
};

export { Invoice as default };
