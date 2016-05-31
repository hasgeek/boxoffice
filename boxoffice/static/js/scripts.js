window.Boxoffice = {};

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
        if(response.readyState === 4) {
          //Add error message
        }
        else if(response.readyState === 0) {
          if(ajaxLoad.retries < 0) {
            errorMsg = "Unable to connect. Please write to us at support@hasgeek.com with your order number";

          } else {
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
          eventName: data.item_collection_name,
          line_items: data.line_items,
          buyer_name: data.buyer_name,
          buyer_email: data.buyer_email,
          buyer_phone: data.buyer_phone
        },
        scrollTop: function(line_item_seq){
          //Scroll to the corresponding line_item.
          var domElem =  order.ractive.nodes[ 'item-' + line_item_seq ];
          $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
        },
        viewTicket: function(event, line_item, line_item_seq) {
          event.original.preventDefault();
          order.ractive.set(line_item + '.toAssign', false);
          order.ractive.scrollTop(line_item_seq);
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

          var assignment = order.ractive.get(line_item +'.assignment');

          if(assignment === 'self') {
            order.ractive.set(line_item + '.assignee.fullname', order.ractive.get('buyer_name'));
            order.ractive.set(line_item + '.assignee.email', order.ractive.get('buyer_email'));
            order.ractive.set(line_item + '.assignee.phone', order.ractive.get('buyer_phone'));
          }
          order.ractive.set(line_item + '.toAssign', true);
        },
        addAttendeDetails: function(event, line_item, line_item_seq, line_item_id) {

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
              rules: 'required|max_length[16]'
            }
          ];

          var attendeeForm = 'attendee-form-' + line_item_seq;

          var formValidator = new FormValidator(attendeeForm, validationConfig, function(errors, event) {
            event.preventDefault();
            if (errors.length > 0) {
              order.ractive.set(line_item + '.errorMsg', errors[0].message);
            } else {
              order.ractive.set(line_item + '.errorMsg', '');
              order.ractive.set(line_item + '.assigningTicket', true);
              order.ractive.sendAttendeDetails(line_item, line_item_seq, line_item_id);
            }
          });
        },
        sendAttendeDetails: function(line_item, line_item_seq, line_item_id) {
          var attendeeForm = 'attendee-details-' + line_item_seq;
          var formElements = $('#'+ attendeeForm).serializeArray();
          var attendeeDetails ={};
          for (var formIndex=0; formIndex < formElements.length; formIndex++) {
            if(formElements[formIndex].value) {
              attendeeDetails[formElements[formIndex].name] = formElements[formIndex].value;
            }
          }
          attendeeDetails['email'] = order.ractive.get(line_item + '.assignee.email');
          attendeeDetails['fullname'] = order.ractive.get(line_item + '.assignee.fullname');
          $.ajax({
            url: Boxoffice.Order.config.assign.urlFor(order.ractive.get('access_token')),
            type: Boxoffice.Order.config.assign.method,
            contentType: 'application/json',
            data: JSON.stringify({
              attendee: attendeeDetails,
              line_item_id: line_item_id
            }),
            timeout: 5000,
            retries: 5,
            retryInterval: 5000,
            success: function(data) {
              order.ractive.set(line_item + '.assigningTicket', false);
              order.ractive.set(line_item + '.toAssign', false);
              order.ractive.set(line_item + '.isTicketAssigned', true);
              order.ractive.scrollTop(line_item_seq);
            },
            error: function(response) {
              var ajaxLoad = this;
              ajaxLoad.retries -= 1;
              if (response.readyState === 4) {
                order.ractive.set(line_item + '.errorMsg', 'Server error');
                order.ractive.set(line_item + '.assigningTicket', false);
              } else if (response.readyState === 0) {
                if(ajaxLoad.retries < 0) {
                  order.ractive.set(line_item + '.errorMsg', "Unable to connect. Please try again later.");
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

  window.Boxoffice.Order.init();

});