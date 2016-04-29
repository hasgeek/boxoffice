/* View list of organizations */
window.Boxoffice.Organizations = {
  config: {
    baseURL: window.location.href,
    view: {
      method: 'GET',
      urlFor: function() {
        return Boxoffice.Organizations.config.baseURL;
      }
    },
    edit: {
      method: 'POST',
      urlFor: function(organization_name) {
        return Boxoffice.Organizations.config.baseURL + organization_name + '/edit';
      }
    },
    add: {
      method: 'POST',
      urlFor: function() {
        return Boxoffice.Organizations.config.baseURL + 'organization/new';
      }
    },
    del: {
      method: 'POST',
      urlFor: function(organization_name) {
        return Boxoffice.Organizations.config.baseURL + organization_name + '/delete';
      }
    }
  },
  init: function() {
    $.ajax({
      url: Boxoffice.Organizations.config.view.urlFor(),
      type: Boxoffice.Organizations.config.view.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success: function(data) {
        window.Boxoffice.Organizations.view(data);
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
            errorMsg = "Unable to connect.";

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
    var organizations = this;
    organizations.ractive = new Ractive({
      el: '#boxoffice-organizations',
      template: '#boxoffice-organizations-template',
      data: {
        organizations: data.organizations
      },
      scrollTop: function(index) {
        //Scroll to the corresponding line_item.
        var domElem =  organizations.ractive.nodes[ 'organization-' + index ];
        $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
      },
      addEmptyOrganization: function() {
        organizations.ractive.push('organizations', {});
      },
      viewDetails: function(event, organization, organization_index) {
        event.original.preventDefault();
        organizations.ractive.set(organization + '.view', false);
        organizations.ractive.scrollTop(organization_index);
      },
      editDetails: function(organization, organization_index) {
        organizations.ractive.set(organization + '.view', true);
      },
      deleteOrganization: function(organization, organization_index) {
        var confirm = window.confirm("Are you sure? This organization will be deleted");
        if(confirm) {
          var org_id = organizations.ractive.get(organization + '.id');
          var data = JSON.stringify({ organization: { id: org_id } });
          organizations.ractive.postToServer(Boxoffice.Organizations.config.del.urlFor(org_id), Boxoffice.Organizations.config.del.method, data, organization, organizations.ractive.refresh);
        }
      },
      addNewField: function(event, organization, fieldtype, organization_index) {
        if(organizations.ractive.get(organization + '.newFields')) {
          organizations.ractive.push(organization + '.newFields', {'fieldName': '', 'fieldValue': '', 'fieldType': fieldtype});
        }
        else {
          organizations.ractive.set(organization + '.newFields', [{'fieldName': '', 'fieldValue': '', 'fieldType': fieldtype}]);
        }
      },
      addDetails: function(event, organization, organization_index, add) {
        var validationConfig = [{
            name: 'title',
            rules: 'required'
          },
          {
            name: 'cin',
            rules: 'required'
          },
          {
            name: 'pan',
            rules: 'required'
          },
          {
            name: 'service_tax_no',
            rules: 'required'
          },
          {
            name: 'website',
            rules: 'required'
          },
          {
            name: 'address',
            rules: 'required'
          },
          {
            name: 'contact_email',
            rules: 'required'
          }
        ];

        var organizationForm = 'organization-form-' + organization_index;

        var formValidator = new FormValidator(organizationForm, validationConfig, function(errors, event) {
          event.preventDefault();
          if (errors.length > 0) {
            organizations.ractive.set(organization + '.errorMsg', errors[0].message);
          } else {
            organizations.ractive.set(organization + '.errorMsg', '');
            organizations.ractive.set(organization + '.updating', true);
            organizations.ractive.sendDetails(organization, organization_index, add);
          }
        });
      },
      sendDetails: function(organization, organization_index, add) {
        var organizationFormID = 'organization-details-' + organization_index;
        var formElements = $('#'+ organizationFormID).serializeArray();
        var organizationDetails = {};
        var url;
        for (var formIndex=0; formIndex < formElements.length; formIndex++) {
          if(formElements[formIndex].value && formElements[formIndex].name) {
            organizationDetails[formElements[formIndex].name] = formElements[formIndex].value;
          }
        }
        if (add) {
          url = Boxoffice.Organizations.config.add.urlFor();
        }
        else {
          organizationDetails.id = organizations.ractive.get(organization + '.id');
          url = Boxoffice.Organizations.config.edit.urlFor(organizationDetails.id);
        }
        var data = JSON.stringify({ organization: organizationDetails });
        organizations.ractive.postToServer(url, Boxoffice.Organizations.config.edit.method, data, organization, organizations.ractive.update);
      },
      update: function(organization, data) {
        organizations.ractive.set(organization + '.updating', false);
        organizations.ractive.set(organization + '.view', false);
        organizations.ractive.set(organization + '.infoMsg', "Details updated");
        organizations.ractive.refresh(organization, organizations);
      },
      refresh: function(organization, data) {
        /* Refresh with item collection details received from server */
        // organizations.ractive.set('organizations', data.organizations);
      },
      postToServer: function(url, type, data, organization, callback) {
        $.ajax({
          url: url,
          type: type,
          contentType: 'application/json',
          data: data,
          timeout: 5000,
          retries: 5,
          dataType: 'json',
          retryInterval: 5000,
          success: function(data) {
            callback(organization, data);
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
                errorMsg = "Unable to connect.";

              } else {
                setTimeout(function() {
                  $.ajax(ajaxLoad);
                }, ajaxLoad.retryInterval);
              }
            }
          }
        });
      },
      oncomplete: function() {
        organizations.ractive.addEmptyOrganization();
      }
    });
  }
};

/* View list of item collections in org */
window.Boxoffice.Itemcollections = {
  config: {
    baseURL: window.location.href,
    view: {
      method: 'GET',
      urlFor: function() {
        return Boxoffice.Itemcollections.config.baseURL;
      }
    },
    edit: {
      method: 'POST',
      urlFor: function(item_collection_id) {
        return Boxoffice.Itemcollections.config.baseURL + '/' + item_collection_id + '/edit';
      }
    },
    add: {
      method: 'POST',
      urlFor: function() {
        return Boxoffice.Itemcollections.config.baseURL + '/item_collection/new';
      }
    },
    del: {
      method: 'POST',
      urlFor: function(item_collection_id) {
        return Boxoffice.Itemcollections.config.baseURL + '/' + item_collection_id + '/delete';
      }
    }
  },
  init: function() {
    $.ajax({
      url: Boxoffice.Itemcollections.config.view.urlFor(),
      type: Boxoffice.Itemcollections.config.view.method,
      timeout: 5000,
      retries: 5,
      dataType: 'json',
      retryInterval: 5000,
      success: function(data) {
        window.Boxoffice.Itemcollections.view(data);
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
            errorMsg = "Unable to connect.";

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
    var itemCollections = this;
    itemCollections.ractive = new Ractive({
      el: '#boxoffice-item-collections',
      template: '#boxoffice-item-collections-template',
      data: {
        item_collections: data.item_collections
      },
      scrollTop: function(index) {
        //Scroll to the corresponding line_item.
        var domElem =  itemCollections.ractive.nodes[ 'item-collection-' + index ];
        $('html,body').animate({ scrollTop: $(domElem).offset().top }, '300');
      },
      addEmptyItemCollection: function() {
        itemCollections.ractive.push('item_collections', {});
      },
      viewDetails: function(event, item_collection, item_collection_index) {
        event.original.preventDefault();
        itemCollections.ractive.set(item_collection + '.view', false);
        itemCollections.ractive.scrollTop(item_collection_index);
      },
      editDetails: function(item_collection, item_collection_index) {
        itemCollections.ractive.set(item_collection + '.view', true);
      },
      deleteItemCollection: function(item_collection, item_collection_index) {
        var confirm = window.confirm("Are you sure? This item collection will be deleted");
        if(confirm) {
          var item_collection_id = itemCollections.ractive.get(item_collection + '.id');
          var data = JSON.stringify({ item_collection: { id: item_collection } });
          itemCollections.ractive.postToServer(Boxoffice.Itemcollections.config.del.urlFor(item_collection_id), Boxoffice.Itemcollections.config.del.method, data, item_collection, itemCollections.ractive.refresh);
        }
      },
      addDetails: function(event, item_collection, item_collection_index, add) {
        var validationConfig = [{
            name: 'title',
            rules: 'required'
          },
          {
            name: 'description',
            rules: 'required'
          }
        ];

        var itemCollectionForm = 'item-collection-form-' + item_collection_index;

        var formValidator = new FormValidator(itemCollectionForm, validationConfig, function(errors, event) {
          event.preventDefault();
          if (errors.length > 0) {
            itemCollections.ractive.set(item_collection + '.errorMsg', errors[0].message);
          } else {
            itemCollections.ractive.set(item_collection + '.errorMsg', '');
            itemCollections.ractive.set(item_collection + '.updating', true);
            itemCollections.ractive.sendDetails(item_collection, item_collection_index, add);
          }
        });
      },
      sendDetails: function(item_collection, item_collection_index, add) {
        var itemCollectionFormID = 'item-collection-details-' + item_collection_index;
        var formElements = $('#'+ itemCollectionFormID).serializeArray();
        var itemCollectionDetails = {};
        var url;
        for (var formIndex=0; formIndex < formElements.length; formIndex++) {
          if(formElements[formIndex].value) {
            itemCollectionDetails[formElements[formIndex].name] = formElements[formIndex].value;
          }
        }
        if (add) {
          url = Boxoffice.Itemcollections.config.add.urlFor();
        }
        else {
          itemCollectionDetails.id = itemCollections.ractive.get(item_collection + '.id');
          url = Boxoffice.Itemcollections.config.edit.urlFor(itemCollectionDetails.id);
        }
        var data = JSON.stringify({ item_collection: itemCollectionDetails });
        itemCollections.ractive.postToServer(url, Boxoffice.Itemcollections.config.edit.method, data, item_collection, itemCollections.ractive.update);
      },
      update: function(item_collection, data) {
        itemCollections.ractive.set(item_collection + '.updating', false);
        itemCollections.ractive.set(item_collection + '.view', false);
        itemCollections.ractive.set(item_collection + '.infoMsg', "Details updated");
        itemCollections.ractive.refresh(item_collection, data);
      },
      refresh: function(item_collection, data) {
        /* Refresh with item collection details received from server */
        // itemCollections.ractive.set('item_collections', data.item_collections);
      },
      postToServer: function(url, type, data, item_collection, callback) {
        $.ajax({
          url: url,
          type: type,
          contentType: 'application/json',
          data: data,
          timeout: 5000,
          retries: 5,
          dataType: 'json',
          retryInterval: 5000,
          success: function(data) {
            callback(item_collection, data);
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
                errorMsg = "Unable to connect.";

              } else {
                setTimeout(function() {
                  $.ajax(ajaxLoad);
                }, ajaxLoad.retryInterval);
              }
            }
          }
        });
      },
      oncomplete: function() {
        itemCollections.ractive.addEmptyItemCollection();
      }
    });
  }
};

/* View line_items in order and assign tickets */
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
        return Boxoffice.Order.config.baseURL + '/assignee/' + access_token + '/assign';
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

          if (assignment === 'self') {
            order.ractive.set(line_item + '.assignee.fullname', order.ractive.get('buyer_name'));
            order.ractive.set(line_item + '.assignee.email', order.ractive.get('buyer_email'));
            order.ractive.set(line_item + '.assignee.phone', order.ractive.get('buyer_phone'));
          }
          else if (assignment === 'other' && !order.ractive.get(line_item + '.assignee.phone')) {
            order.ractive.set(line_item + '.assignee.phone', '+91');
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
              rules: 'required|max_length[16]|callback_validate_phone'
            }];

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
        sendAttendeDetails: function(line_item, line_item_seq, line_item_id) {
          var attendeeForm = 'attendee-details-' + line_item_seq;
          var formElements = $('#'+ attendeeForm).serializeArray();
          var attendeeDetails ={};
          for (var formIndex=0; formIndex < formElements.length; formIndex++) {
            if(formElements[formIndex].value) {
              attendeeDetails[formElements[formIndex].name] = formElements[formIndex].value;
            }
          }
          attendeeDetails.email = order.ractive.get(line_item + '.assignee.email');
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
});
