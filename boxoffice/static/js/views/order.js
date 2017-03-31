window.Boxoffice = window.Boxoffice || {};

window.Boxoffice.Order = {
  config: {
    baseURL: window.location.origin,
    order: {
      method: 'GET',
      urlFor: function() {
        return window.location.href;
      }
    },
    assign: {
      method: 'POST',
      urlFor: function(accessToken) {
        return Boxoffice.Order.config.baseURL + '/participant/' + accessToken + '/assign';
      }
    }
  },
  init: function() {
    $.ajax({
      url: Boxoffice.Order.config.order.urlFor(),
      type: Boxoffice.Order.config.order.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success: function(data) {
        window.Boxoffice.Order.view(data);
      },
      error: function(response) {
        var ajaxLoad = this;
        ajaxLoad.retries -= 1;
        var errorMsg;
        if (response.readyState === 4) {
          errorMsg = "Server error. ";
          $("#error-description").html(errorMsg);
        }
        else if (response.readyState === 0) {
          if (ajaxLoad.retries < 0) {
            errorMsg = "Unable to connect. Please try again later.";
            $("#notify-msg").html(errorMsg);
          }
          else {
            setTimeout(function() {
              $.ajax(ajaxLoad);
            }, ajaxLoad.retryInterval);
          }
        }
      }
    });
  },
  view: function(data) {
    var order = this;
    order.component = new Ractive({
      el: '#boxoffice-order',
      template: '#boxoffice-ticket-template',
      data: {
        orderId: data.order_id,
        accessToken: data.access_token,
        eventName: data.item_collection_name,
        lineItems: data.line_items
      },
      scrollTop: function(lineItemSeq){
        //Scroll to the corresponding line_item.
        var domElem =  order.component.nodes[ 'item-' + lineItemSeq ];
        $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
      },
      viewTicket: function(event, lineItem, lineItemSeq) {
        event.original.preventDefault();
        order.component.set(lineItem + '.toAssign', false);
        order.component.scrollTop(lineItemSeq);
      },
      inputFieldEdit: function(event, lineItem) {
        if (event.node.value) {
          event.node.classList.add('filled');
        }
        else {
          event.node.classList.remove('filled');
        }
      },
      assign: function(event, lineItem, edit) {
        event.original.preventDefault();
        if (!edit) {
          order.component.set(lineItem + '.assignee.fullname', "");
          order.component.set(lineItem + '.assignee.email', "");
          order.component.set(lineItem + '.assignee.phone', "+91");
        }
        order.component.set(lineItem + '.toAssign', true);
      },
      addAssigneeDetails: function(event, lineItem, lineItemSeq, lineItemId) {

        var validationConfig = [{
            name: 'fullname',
            rules: 'required'
          },
          {
            name: 'email',
            rules: 'required|valid_email'
          },
          {
            name: 'phone',
            rules: 'required|callback_validate_phone'
          }
        ];

        var assigneeForm = 'assignee-form-' + lineItemSeq;

        var formValidator = new FormValidator(assigneeForm, validationConfig, function(errors, event) {
          event.preventDefault();
          order.component.set(lineItem +  '.assignee.errormsg', '');
          if (errors.length > 0) {
            order.component.set(lineItem +  '.assignee.errormsg.'+ errors[0].name, errors[0].message);
            order.component.scrollTop(lineItemSeq);
          }
          else {
            order.component.set(lineItem + '.assigningTicket', true);
            order.component.sendAssigneeDetails(lineItem, lineItemSeq, lineItemId);
          }
        });

        formValidator.setMessage('required', 'Please fill out the %s field');
        formValidator.setMessage('valid_email', 'Please enter a valid email');
 
        formValidator.registerCallback('validate_phone', function(phone) {
          //Remove all punctations (except +) and letters
          phone = phone.replace(/[^0-9+]/g,'');
          order.component.set(lineItem + '.assignee.phone', phone);

          var validPhone = /^\+[0-9]+$/;

          if (phone.length > 16) {
            formValidator.setMessage('validate_phone', 'Please enter a valid mobile number');
            return false;
          }
          else if (phone.match(validPhone)) {
            //Indian number starting with '+91'
            if (phone.indexOf('+91') === 0 && phone.length != 13) {
              formValidator.setMessage('validate_phone', 'Please enter a valid Indian mobile number');
              return false;
            }
          }
          else {
            formValidator.setMessage('validate_phone', "Please prefix your phone number with '+' and country code.");
            return false;
          }
        });
      },
      sendAssigneeDetails: function(lineItem, lineItemSeq, lineItemId) {
        var assigneeForm = 'assignee-details-' + lineItemSeq;
        var formElements = $('#'+ assigneeForm).serializeArray();
        var assigneeDetails ={};
        for (var formIndex=0; formIndex < formElements.length; formIndex++) {
          if (formElements[formIndex].value) {
            assigneeDetails[formElements[formIndex].name] = formElements[formIndex].value;
          }
        }

        $.ajax({
          url: Boxoffice.Order.config.assign.urlFor(order.component.get('accessToken')),
          type: Boxoffice.Order.config.assign.method,
          contentType: 'application/json',
          data: JSON.stringify({
            assignee: assigneeDetails,
            line_item_id: lineItemId
          }),
          timeout: 30000,
          retries: 5,
          retryInterval: 30000,
          success: function(data) {
            order.component.set(lineItem + '.assigningTicket', false);
            order.component.set(lineItem + '.toAssign', false);
            order.component.set(lineItem + '.isTicketAssigned', true);
            order.component.scrollTop(lineItemSeq);
          },
          error: function(response) {
            var ajaxLoad = this;
            ajaxLoad.retries -= 1;
            if (response.readyState === 4) {
              order.component.set(lineItem + '.errorMsg', 'Server error');
              order.component.set(lineItem + '.assigningTicket', false);
            } else if (response.readyState === 0) {
              if (ajaxLoad.retries < 0) {
                order.component.set(lineItem + '.errorMsg', "Unable to connect. Please try again later.");
                order.component.set(lineItem + '.assigningTicket', false);
              } else {
                setTimeout(function() {
                  $.ajax(ajaxLoad);
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

  window.Boxoffice.Order.init();

});
