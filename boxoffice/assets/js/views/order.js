/* eslint-disable no-unused-vars */
import { xhrRetry, getFormJSObject } from '../models/util';
import { TicketAssignmentTemplate } from '../templates/ticket_assigment.html';

const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');
const FormValidator = require('validate-js');

export const Order = {
  config: {
    baseURL: window.location.origin,
    view: {
      method: 'GET',
      urlFor() {
        return window.location.href;
      },
    },
    assign: {
      method: 'POST',
      urlFor(accessToken) {
        return `${Order.config.baseURL}/participant/${accessToken}/assign`;
      },
    },
  },
  init() {
    $.ajax({
      url: Order.config.view.urlFor(),
      type: Order.config.view.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success(data) {
        Order.view(data);
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
    const order = this;
    order.ticketComponent = new Ractive({
      el: '#boxoffice-order',
      template: TicketAssignmentTemplate,
      transitions: { fly },
      data: {
        orderId: data.order_id,
        access_token: data.access_token,
        eventName: data.menu_name,
        lineItems: data.line_items,
        buyer_name: data.buyer_name,
        buyer_email: data.buyer_email,
        buyer_phone: data.buyer_phone,
        formatDate(dateTimeString) {
          return new Date(dateTimeString).toDateString();
        },
      },
      scrollTop(lineItemSeq) {
        // Scroll to the corresponding lineItem.
        const domElem = order.ticketComponent.nodes[`item-${lineItemSeq}`];
        $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
      },
      viewTicket(event, lineItem, lineItemSeq) {
        event.original.preventDefault();
        order.ticketComponent.set(`${lineItem}.toAssign`, false);
        order.ticketComponent.scrollTop(lineItemSeq);
      },
      inputFieldEdit(event, lineItem) {
        if (event.node.value) {
          event.node.classList.add('filled');
        } else {
          event.node.classList.remove('filled');
        }
      },
      assign(event, lineItem, edit) {
        event.original.preventDefault();
        if (!edit) {
          order.ticketComponent.set(`${lineItem}.assignee.fullname`, '');
          order.ticketComponent.set(`${lineItem}.assignee.email`, '');
          order.ticketComponent.set(`${lineItem}.assignee.phone`, '+91');
        }
        order.ticketComponent.set(`${lineItem}.toAssign`, true);
      },
      addAttendeeDetails(event, lineItem, lineItemSeq, lineItemId) {
        const validationConfig = [
          {
            name: 'fullname',
            rules: 'required',
          },
          {
            name: 'email',
            rules: 'required|valid_email',
          },
          {
            name: 'phone',
            rules: 'required|callback_validate_phone',
          },
        ];

        const attendeeForm = `attendee-form-${lineItemSeq}`;

        const formValidator = new FormValidator(
          attendeeForm,
          validationConfig,
          (errors, e) => {
            e.preventDefault();
            order.ticketComponent.set(`${lineItem}.errorMsg`, '');
            order.ticketComponent.set(`${lineItem}.assignee.errormsg`, '');
            if (errors.length > 0) {
              order.ticketComponent.set(
                `${lineItem}.assignee.errormsg.${errors[0].name}`,
                errors[0].message
              );
              order.ticketComponent.scrollTop(lineItemSeq);
            } else {
              order.ticketComponent.set(`${lineItem}.assigningTicket`, true);
              order.ticketComponent.sendAttendeeDetails(
                lineItem,
                lineItemSeq,
                lineItemId
              );
            }
          }
        );

        formValidator.setMessage('required', 'Please fill out the %s field');
        formValidator.setMessage('valid_email', 'Please enter a valid email');

        formValidator.registerCallback('validate_phone', (inPhone) => {
          // Remove all punctations (except +) and letters
          const phone = inPhone.replace(/[^0-9+]/g, '');
          order.ticketComponent.set(`${lineItem}.assignee.phone`, phone);

          const validPhone = /^\+[0-9]+$/;

          if (phone.length > 16) {
            formValidator.setMessage(
              'validate_phone',
              'Please enter a valid mobile number'
            );
            return false;
          }
          if (phone.match(validPhone)) {
            // Indian number starting with '+91'
            if (phone.indexOf('+91') === 0 && phone.length !== 13) {
              formValidator.setMessage(
                'validate_phone',
                'Please enter a valid Indian mobile number'
              );
              return false;
            }
          } else {
            formValidator.setMessage(
              'validate_phone',
              "Please prefix your phone number with '+' and country code."
            );
            return false;
          }
          return true;
        });
      },
      sendAttendeeDetails(lineItem, lineItemSeq, lineItemId) {
        const attendeeForm = `#attendee-details-${lineItemSeq}`;
        const attendeeDetails = getFormJSObject(attendeeForm);

        $.ajax({
          url: Order.config.assign.urlFor(order.ticketComponent.get('access_token')),
          type: Order.config.assign.method,
          contentType: 'application/json',
          data: JSON.stringify({
            attendee: attendeeDetails,
            line_item_id: lineItemId,
            csrf_token: $('meta[name=csrf-token]').attr('content'),
          }),
          timeout: 30000,
          retries: 5,
          retryInterval: 30000,
          success(successData) {
            order.ticketComponent.set(`${lineItem}.assigningTicket`, false);
            order.ticketComponent.set(`${lineItem}.toAssign`, false);
            order.ticketComponent.set(`${lineItem}.isTicketAssigned`, true);
            order.ticketComponent.scrollTop(lineItemSeq);
          },
          error(response) {
            const ajaxLoad = this;
            function onServerError() {
              let errorMsg;
              if (
                response.responseJSON !== undefined &&
                response.responseJSON.error_description !== undefined
              ) {
                errorMsg = response.responseJSON.error_description;
                response.responseJSON.error_details.forEach((error) => {
                  order.ticketComponent.set(
                    `${lineItem}.assignee.errormsg.${error}`,
                    response.responseJSON.error_details[error][0]
                  );
                });
              } else {
                errorMsg = 'Server error.';
              }
              order.ticketComponent.set(`${lineItem}.errorMsg`, errorMsg);
              order.ticketComponent.set(`${lineItem}.assigningTicket`, false);
            }
            function onNetworkError() {
              order.ticketComponent.set(
                `${lineItem}.errorMsg`,
                'Unable to connect. Please try again later.'
              );
              order.ticketComponent.set(`${lineItem}.assigningTicket`, false);
            }
            ajaxLoad.retries -= 1;
            xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
          },
        });
      },
    });
  },
};

export { Order as default };
