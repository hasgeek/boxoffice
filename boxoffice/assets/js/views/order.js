import { xhrRetry, getFormJSObject } from '../models/util.js';
import { TicketAssignmentTemplate } from '../templates/ticket_assigment.html.js';
var FormValidator = require('validate-js');

export const Order = {
  config: {
    baseURL: window.location.origin,
    view: {
      method: 'GET',
      urlFor: function () {
        return window.location.href;
      },
    },
    assign: {
      method: 'POST',
      urlFor: function (access_token) {
        return (
          Order.config.baseURL + '/participant/' + access_token + '/assign'
        );
      },
    },
  },
  init: function () {
    $.ajax({
      url: Order.config.view.urlFor(),
      type: Order.config.view.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success: function (data) {
        Order.view(data);
      },
      error: function (response) {
        var ajaxLoad = this;
        var onServerError = function () {
          var errorMsg = 'Server error. ';
          $('#error-description').html(errorMsg);
        };
        var onNetworkError = function () {
          var errorMsg = 'Unable to connect. Please try again later.';
          $('#notify-msg').html(errorMsg);
        };
        ajaxLoad.retries -= 1;
        xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
      },
    });
  },
  view: function (data) {
    var order = this;
    order.ticketComponent = new Ractive({
      el: '#boxoffice-order',
      template: TicketAssignmentTemplate,
      data: {
        order_id: data.order_id,
        access_token: data.access_token,
        eventName: data.item_collection_name,
        line_items: data.line_items,
        buyer_name: data.buyer_name,
        buyer_email: data.buyer_email,
        buyer_phone: data.buyer_phone,
        formatDate: function (dateTimeString) {
          return new Date(dateTimeString).toDateString();
        },
      },
      scrollTop: function (line_item_seq) {
        //Scroll to the corresponding line_item.
        var domElem = order.ticketComponent.nodes['item-' + line_item_seq];
        $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
      },
      viewTicket: function (event, line_item, line_item_seq) {
        event.original.preventDefault();
        order.ticketComponent.set(line_item + '.toAssign', false);
        order.ticketComponent.scrollTop(line_item_seq);
      },
      inputFieldEdit: function (event, line_item) {
        if (event.node.value) {
          event.node.classList.add('filled');
        } else {
          event.node.classList.remove('filled');
        }
      },
      assign: function (event, line_item, edit) {
        event.original.preventDefault();
        if (!edit) {
          order.ticketComponent.set(line_item + '.assignee.fullname', '');
          order.ticketComponent.set(line_item + '.assignee.email', '');
          order.ticketComponent.set(line_item + '.assignee.phone', '+91');
        }
        order.ticketComponent.set(line_item + '.toAssign', true);
      },
      addAttendeeDetails: function (
        event,
        line_item,
        line_item_seq,
        line_item_id
      ) {
        var validationConfig = [
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

        var attendeeForm = 'attendee-form-' + line_item_seq;

        var formValidator = new FormValidator(
          attendeeForm,
          validationConfig,
          function (errors, event) {
            event.preventDefault();
            order.ticketComponent.set(line_item + '.errorMsg', '');
            order.ticketComponent.set(line_item + '.assignee.errormsg', '');
            if (errors.length > 0) {
              order.ticketComponent.set(
                line_item + '.assignee.errormsg.' + errors[0].name,
                errors[0].message
              );
              order.ticketComponent.scrollTop(line_item_seq);
            } else {
              order.ticketComponent.set(line_item + '.assigningTicket', true);
              order.ticketComponent.sendAttendeeDetails(
                line_item,
                line_item_seq,
                line_item_id
              );
            }
          }
        );

        formValidator.setMessage('required', 'Please fill out the %s field');
        formValidator.setMessage('valid_email', 'Please enter a valid email');

        formValidator.registerCallback('validate_phone', function (phone) {
          //Remove all punctations (except +) and letters
          phone = phone.replace(/[^0-9+]/g, '');
          order.ticketComponent.set(line_item + '.assignee.phone', phone);

          var validPhone = /^\+[0-9]+$/;

          if (phone.length > 16) {
            formValidator.setMessage(
              'validate_phone',
              'Please enter a valid mobile number'
            );
            return false;
          } else if (phone.match(validPhone)) {
            //Indian number starting with '+91'
            if (phone.indexOf('+91') === 0 && phone.length != 13) {
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
        });
      },
      sendAttendeeDetails: function (line_item, line_item_seq, line_item_id) {
        var attendeeForm = '#' + 'attendee-details-' + line_item_seq;
        var attendeeDetails = getFormJSObject(attendeeForm);

        $.ajax({
          url: Order.config.assign.urlFor(
            order.ticketComponent.get('access_token')
          ),
          type: Order.config.assign.method,
          contentType: 'application/json',
          data: JSON.stringify({
            attendee: attendeeDetails,
            line_item_id: line_item_id,
            csrf_token: $('meta[name=csrf-token]').attr('content'),
          }),
          timeout: 30000,
          retries: 5,
          retryInterval: 30000,
          success: function (data) {
            order.ticketComponent.set(line_item + '.assigningTicket', false);
            order.ticketComponent.set(line_item + '.toAssign', false);
            order.ticketComponent.set(line_item + '.isTicketAssigned', true);
            order.ticketComponent.scrollTop(line_item_seq);
          },
          error: function (response) {
            var ajaxLoad = this;
            var onServerError = function () {
              var errorMsg, error;
              if (
                response.responseJSON !== undefined &&
                response.responseJSON.error_description !== undefined
              ) {
                errorMsg = response.responseJSON.error_description;
                for (error in response.responseJSON.error_details) {
                  order.ticketComponent.set(
                    line_item + '.assignee.errormsg.' + error,
                    response.responseJSON.error_details[error][0]
                  );
                }
              } else {
                errorMsg = 'Server error.';
              }
              order.ticketComponent.set(line_item + '.errorMsg', errorMsg);
              order.ticketComponent.set(line_item + '.assigningTicket', false);
            };
            var onNetworkError = function () {
              order.ticketComponent.set(
                line_item + '.errorMsg',
                'Unable to connect. Please try again later.'
              );
              order.ticketComponent.set(line_item + '.assigningTicket', false);
            };
            ajaxLoad.retries -= 1;
            xhrRetry(ajaxLoad, response, onServerError, onNetworkError);
          },
        });
      },
    });
  },
};
