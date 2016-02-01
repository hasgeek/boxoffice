window.Boxoffice = {};

$(function(){
  var boxoffice = window.Boxoffice;

  var handleRazorpay = function(){
    var options = {
      "key": "YOUR_KEY_ID",
      "amount": "2000",
      "name": "Merchant Name",
      "description": "Purchase Description",
      "image": "/your_logo.png",
      "handler": function (response){
        console.log(response.razorpay_payment_id);
      },
      "prefill": {
        "name": "Harshil Mathur",
        "email": "harshil@razorpay.com"
      },
      "notes": {
        "address": "Hello World"
      },
      "theme": {
        "color": "#F37254"
      }
    };
    
    var rzp1 = new Razorpay(options);

    $("#rzp-button1").click(function(e){
      rzp1.open();
      e.preventDefault();
    });
  }

  boxoffice.init = function(config){
    $.ajax({
      url: config.url,
      crossDomain: true,
      dataType: 'jsonp'
    }).done(function(data){
      boxoffice.ractive = new Ractive({
        el: 'boxoffice-widget',
        template: data.html,
        data: {
          order: {
            //{item_id: 1, quantity: 4, price: xx, discount, tax: xxxx}
            id: '',
            lineItems:[],
            user_id: ''
          },
          tabs: {
            selectItems: {
              id: 'boxoffice-selectItems',
              label: 'Select Tickets',
              active: true,
              complete: false,
              section: {
                categories: data.categories
              }
            },
            payment: {
              id: 'boxoffice-payment',
              label: 'Payment',
              active: false,
              complete: false,
              section: {
                buyer: {
                  email: '',
                  fullname: '',
                  phone: ''
                }
              }
            },
            attendees: {
              id: 'boxoffice-attendee-details',
              label: 'Attendee Details',
              active: false,
              complete: false,
              section: {
                attendees: [
                ]
              }
            }
          },
        },
        oncomplete: function(){
          // on checkout
          // add/remove line items when somebody hits continue
          
          // on proceed to payment
          // update the status of the order to 'Sales Order'
          // start the razorpay widget

          // how do we associate the payment id with the order id?
        }
      })
    })
  }
});