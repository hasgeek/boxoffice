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
      urlFor: function(access_token) {
        return Boxoffice.Order.config.baseURL + '/participant/' + access_token + '/assign';
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
    order.ractive = new Ractive({
      el: '#boxoffice-order',
      template: '#boxoffice-ticket-template',
      data: {
        order_id: data.order_id,
        access_token: data.access_token,
        line_items: data.line_items,
        buyer_name: data.buyer_name,
        buyer_email: data.buyer_email,
        buyer_phone: data.buyer_phone
      },
      scrollTop: function(line_item_seq){
        //Scroll to the corresponding line_item.
        var dom_elem =  order.ractive.nodes[ 'item-' + line_item_seq ];
        $('html,body').animate({ scrollTop: $(dom_elem).offset().top }, '300');
      },
      viewTicket: function(event, line_item, line_item_seq) {
        event.original.preventDefault();
        order.ractive.set(line_item + '.toAssign', false);
        order.ractive.scrollTop(line_item_seq);
      },
      inputFieldEdit: function(event, line_item) {
        if (event.node.value) {
          event.node.classList.add('filled');
        }
        else {
          event.node.classList.remove('filled');
        }
      },
      assign: function(event, line_item, edit) {
        event.original.preventDefault();

        //On initial assignment of ticket, fill the ticket with details
        // depending on option(self/other) selected by the user
        if (!edit) {
          var assignment = order.ractive.get(line_item +'.assignment');

          if (assignment === 'self') {
            order.ractive.set(line_item + '.assignee.fullname', order.ractive.get('buyer_name'));
            order.ractive.set(line_item + '.assignee.email', order.ractive.get('buyer_email'));
            order.ractive.set(line_item + '.assignee.phone', order.ractive.get('buyer_phone'));
          }
          else {
            order.ractive.set(line_item + '.assignee.fullname', "");
            order.ractive.set(line_item + '.assignee.email', "");
            order.ractive.set(line_item + '.assignee.phone', "+91");
          }
        }
        order.ractive.set(line_item + '.toAssign', true);
      },
      addAssigneeDetails: function(event, line_item, line_item_seq, line_item_id) {

        var validation_config = [{
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

        var assignee_form = 'assignee-form-' + line_item_seq;

        var form_validator = new FormValidator(assignee_form, validation_config, function(errors, event) {
          event.preventDefault();
          order.ractive.set(line_item +  '.assignee.errormsg', '');
          order.ractive.set(line_item + '.errorMsg', '');
          if (errors.length > 0) {
            order.ractive.set(line_item +  '.assignee.errormsg.'+ errors[0].name, errors[0].message);
            order.ractive.scrollTop(line_item_seq);
          }
          else {
            order.ractive.set(line_item + '.assigningTicket', true);
            order.ractive.sendAssigneeDetails(line_item, line_item_seq, line_item_id);
          }
        });

        form_validator.setMessage('required', 'Please fill out the %s field');
        form_validator.setMessage('valid_email', 'Please enter a valid email');
 
        form_validator.registerCallback('validate_phone', function(phone) {
          //Remove all punctations (except +) and letters
          phone = phone.replace(/[^0-9+]/g,'');
          order.ractive.set(line_item + '.assignee.phone', phone);

          var validPhone = /^\+[0-9]+$/;

          if (phone.length > 16) {
            form_validator.setMessage('validate_phone', 'Please enter a valid mobile number');
            return false;
          }
          else if (phone.match(validPhone)) {
            //Indian number starting with '+91'
            if (phone.indexOf('+91') === 0 && phone.length != 13) {
              form_validator.setMessage('validate_phone', 'Please enter a valid Indian mobile number');
              return false;
            }
          }
          else {
            form_validator.setMessage('validate_phone', "Please prefix your phone number with '+' and country code.");
            return false;
          }
        });
      },
      sendAssigneeDetails: function(line_item, line_item_seq, line_item_id) {
        var assignee_form = 'assignee-details-' + line_item_seq;
        var form_elements = $('#'+ assignee_form).serializeArray();
        var assignee_details ={};

        for (var form_index=0; form_index < form_elements.length; form_index++) {
          if (form_elements[form_index].value) {
            assignee_details[form_elements[form_index].name] = form_elements[form_index].value;
          }
        }

        $.ajax({
          url: Boxoffice.Order.config.assign.urlFor(order.ractive.get('access_token')),
          type: Boxoffice.Order.config.assign.method,
          contentType: 'application/json',
          data: JSON.stringify({
            assignee: assignee_details,
            line_item_id: line_item_id
          }),
          timeout: 30000,
          retries: 5,
          retryInterval: 30000,
          success: function(data) {
            order.ractive.set(line_item + '.assigningTicket', false);
            order.ractive.set(line_item + '.toAssign', false);
            order.ractive.set(line_item + '.isTicketAssigned', true);
            order.ractive.scrollTop(line_item_seq);
            order.ractive.set(line_item + '.assignee', data.result.assignee);
          },
          error: function(response) {
            var ajaxLoad = this;
            ajaxLoad.retries -= 1;
            if (response.readyState === 4) {
              var error_text;
              if (response.status === 500) {
                error_text = "Server Error";
              }
              else {
                error_text = JSON.parse(response.responseText).error_description;
              }
              order.ractive.set(line_item + '.errorMsg', error_text);
              order.ractive.set(line_item + '.assigningTicket', false);
            } else if (response.readyState === 0) {
              if (ajaxLoad.retries < 0) {
                order.ractive.set(line_item + '.errorMsg', "Unable to connect. Please try again later.");
                order.ractive.set(line_item + '.assigningTicket', false);
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
