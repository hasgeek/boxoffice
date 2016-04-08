window.Boxoffice = {};

window.Boxoffice.config = {
  baseURL: window.location.origin,
  order: {
    method: 'GET',
    urlFor: function() {
      return window.location.href;
    }
  },
  assign: {
    method: 'POST',
    urlFor: function(order_id) {
      return Boxoffice.config.baseURL + '/participant/' + order_id + '/assign';
    }
  }
};

window.Boxoffice.Body = {
  init: function() {
    $.ajax({
      url: Boxoffice.config.order.urlFor(),
      type: Boxoffice.config.order.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success: function(data) {
        console.log("Order details:", data);
        window.Boxoffice.Order.init(data);
      },
      error: function(response) {
        var ajaxLoad = this;
        ajaxLoad.retries -= 1;
        var errorMsg;
        if(response.readyState === 4) {
          //Add error message
        }
        else if(response.readyState === 0) {
          if(ajaxLoad.retries < 0) {
            errorMsg = "Unable to connect. Please write to us at support@hasgeek.com with your order id " + boxoffice.ractive.get('order.order_id') + ".";

          } else {
            setTimeout(function() {
              $.ajax(ajaxLoad);
            }, ajaxLoad.retryInterval);
          }
        }
      }
    });
  }
};

window.Boxoffice.Order = {
  init: function(data) {
    var order = this;
    order.ractive = new Ractive({
        el: '#boxoffice-order',
        template: '#boxoffice-ticket-template',
        data: {
          order_id: data.order_id,
          access_token: data.access_token,
          eventName: data.item_collection_name,
          line_items: data.line_items,
          buyer_name: data.buyer_name,
          buyer_email: data.buyer_email,
          buyer_phone: data.buyer_phone
        },
        scrollTop: function(line_item_id){
          //Scroll to the corresponding line_item.
          var domElem =  order.ractive.nodes[ 'item-' + line_item_id ];
          $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
        },
        viewTicket: function(event, line_item, line_item_id) {
          event.original.preventDefault();
          order.ractive.set(line_item + '.toAssign', false);
          order.ractive.scrollTop(line_item_id);
        },
        inputFieldEdit: function(event, line_item) {
          if(event.node.value) {
            event.node.classList.add('filled');
          }
          else {
            event.node.classList.remove('filled');
          }
        },
        assign: function(event, line_item) {
          event.original.preventDefault();

          var assignee = order.ractive.get(line_item +'.assignee');

          if(assignee === 'self') {
            order.ractive.set(line_item + '.name', order.ractive.get('buyer_name'));
            order.ractive.set(line_item + '.email', order.ractive.get('buyer_email'));
            order.ractive.set(line_item + '.phone', order.ractive.get('buyer_phone'));
          }
          else {
            order.ractive.set(line_item + '.phone', '+91');
          }
          order.ractive.set(line_item + '.toAssign', true);
        },
        addAttendeDetails: function(event, line_item, line_item_id) {

          var validationConfig = [{
              name: 'name',
              rules: 'required'
            },
            {
              name: 'email',
              rules: 'required|valid_email'
            },
            {
              name: 'phone',
              rules: 'required|max_length[16]|callback_validate_phone'
            }
          ];

          var attendeeForm = 'attendee-form-' + line_item_id;

          var formValidator = new FormValidator(attendeeForm, validationConfig, function(errors, event) {
            event.preventDefault();
            if (errors.length > 0) {
              console.log("Form validation errors", errors[0].message);
              order.ractive.set(line_item + '.errorMsg', errors[0].message);
            } else {
              order.ractive.set(line_item + '.errorMsg', '');
              order.ractive.set(line_item + '.assigningTicket', true);
              order.ractive.sendAttendeDetails(line_item, line_item_id);
            }
          });

          formValidator.registerCallback('validate_phone', function(phone) {
            var validPhone = /^\+[0-9]+$/;
            if (phone.match(validPhone)) {
              //Indian number starting with '+91'
              if (phone.indexOf('+91') === 0 && phone.length != 13) {
                formValidator.setMessage('validate_phone', 'This does not appear to be a valid Indian mobile number');
                return false;
              }
            } else {
              formValidator.setMessage('validate_phone', 'Phone number must be in international format with a leading + symbol');
              return false;
            }
          });
        },
        sendAttendeDetails: function(line_item, line_item_id) {
          var attendeeForm = 'attendee-details-' + line_item_id
          var formElements = $('#'+ attendeeForm).serializeArray();
          var attendeeDetails ={};
          for (var formIndex=0; formIndex < formElements.length; formIndex++) {
            if(formElements[formIndex].value) {
              attendeeDetails[formElements[formIndex].name] = formElements[formIndex].value;
            }
          }
          console.log("Sending participant details to server:", attendeeDetails);
          $.ajax({
            url: Boxoffice.config.assign.urlFor(order.ractive.get('order_id')),
            type: Boxoffice.config.assign.method,
            dataType: 'json',
            data: JSON.stringify({
              attendee: attendeeDetails
            }),
            timeout: 5000,
            retries: 5,
            retryInterval: 5000,
            success: function(data) {
              order.ractive.set(line_item + '.assigningTicket', false);
              order.ractive.set(line_item + '.toAssign', false);
              order.ractive.set(line_item + '.isTicketAssigned', true);
              order.ractive.scrollTop(line_item_id);
            },
            error: function(response) {
              var ajaxLoad = this;
              ajaxLoad.retries -= 1;
              if (response.readyState === 4) {
                order.ractive.set(line_item + '.errorMsg', 'Server error');
                order.ractive.set(line_item + '.assigningTicket', false);
              } else if (response.readyState === 0) {
                if(ajaxLoad.retries < 0) {
                  order.ractive.set(line_item + '.errorMsg', "Unable to connect. Please try again later.")
                  order.ractive.set(line_item + '.assigningTicket', false);
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

$(function() {
  Ractive.DEBUG = false;

  window.Boxoffice.Body.init();

});