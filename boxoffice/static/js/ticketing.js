window.Boxoffice = {};

Boxoffice.Config = {
};

Boxoffice.Body = {
};

Boxoffice.PaymentProgress = {
  init: function() {
    var paymentprogress = this;

    paymentprogress.ractive = new Ractive ({
      el: 'payment-stages',
      template: '#payment-stages-template',
      data: {
        selectTicketActive: true,
        selectTicketCompleted: false,
        buyerDetailsActive: false,
        buyerDetailsCompleted: false,
        paymentDetailsActive: false,
        paymentDetailsCompleted: false,
        attendeeDetailsActive: false,
        attendeeDetailsCompleted: false
      },
      oncomplete: function() {

        amplify.subscribe('buyer-details-activate', function() {
          paymentprogress.ractive.set('selectTicketActive', false);
          paymentprogress.ractive.set('selectTicketCompleted', true);
          paymentprogress.ractive.set('buyerDetailsActive', true);
        });

        amplify.subscribe('payment-details-activate', function() {
          paymentprogress.ractive.set('buyerDetailsActive', false);
          paymentprogress.ractive.set('buyerDetailsCompleted', true);
          paymentprogress.ractive.set('paymentDetailsActive', true);
        });

        amplify.subscribe('attendee-details-activate', function() {
          paymentprogress.ractive.set('paymentDetailsActive', false);
          paymentprogress.ractive.set('paymentDetailsCompleted', true);
          paymentprogress.ractive.set('attendeeDetailsActive', true);
        });

        $('.progress-indicator li').on('click', function(event) {
          event.preventDefault();
          var section = $(this).data('target');
          $(section).slideDown();
          if($(section).parent('div').hasClass('active') || $(section).parent('div').hasClass('completed')) {
            var sectionPos = $(section).offset().top;
            $('html,body').animate({scrollTop:sectionPos}, '900');
          }
        });
      }
    });
  }
}

Boxoffice.TicketSelection = {
  init: function() {
    var ticketSelection = this;

    ticketSelection.ractive = new Ractive ({
      el: 'ticket-selection',
      template: '#ticket-selection-template',
      data: { 
        eventName: '',
        items: '',
        serviceTax: 0,
        totalPrice: 0,
        discountCodeLoading: false,
        discountCodeError: false,
        discountCodeMessage: '',
        selectedTickets: [],
        stageComplete: false,
        visible: true,
        errorMsg: "",
        availableTickets: function(qty) {
          var tickets = [];
          if(qty > 10) {
            qty = 10;
          }
          for(var ticket = 0; ticket <= qty; ticket ++ ) {
            tickets.push(ticket);
          }
          return tickets;
        }
      },
      requestItems: function() {
        $.ajax({
          type: 'GET',
          url: '/items.json',
          dataType: 'json',
          timeout: 5000,
          success: function(data) {
            ticketSelection.ractive.set('eventName', data.event);
            window.Boxoffice.Config.event = data.event;
            ticketSelection.ractive.set('items', data.items);
            ticketSelection.ractive.set('errorMsg', '');
          },
          error: function() {
            ticketSelection.ractive.set('errorMsg', 'Something went wrong. Loading again.');
          }
        });
      },
      oncomplete: function() {
        //Initial request of items
        ticketSelection.ractive.requestItems();

        $('#ticket-selection').on('change', '.ticket-qty', function() {
          var ticketSelected = false;
          var totalprice = 0;
          var serviceTax = 0;
          var selectedTickets = [];
          $.each($('.ticket-qty'), function(index, ticketSelectElem) {
            var ticketCatgeoryQty = {}
            var ticketQty =  parseInt($(ticketSelectElem).val(), 10);
            if(ticketQty > 0) {
              totalprice = totalprice + ($(ticketSelectElem).val() * $(ticketSelectElem).data('ticketprice'));
              ticketCatgeoryQty.id = $(ticketSelectElem).attr('id');
              ticketCatgeoryQty.qty = ticketQty;
              selectedTickets.push(ticketCatgeoryQty);
              ticketSelected = true;
            }
          });

          //stub code
          console.log('Ticket JSON send to server',{ tickets: selectedTickets } );
          serviceTax = Math.round(0.145 * totalprice);

          ticketSelection.ractive.set('selectedTickets', selectedTickets);
          //Request server to receive serviceTax and totalPrice
          if(ticketSelected) {
            ticketSelection.ractive.set('errorMsg', '');
            /*
            $.ajax({
              type: 'POST',
              url: '',
              data: {
                tickets: selectedTickets,
              },
              dataType: 'json',
              timeout: 5000,
              success: function(data) {
                ticketSelection.ractive.set('stageComplete', true);
                ticketSelection.ractive.set('serviceTax', data.serviceTax);
                ticketSelection.ractive.set('totalPrice', data.totalprice);
                
              }
            }); */
            
            //stub
            console.log('JSON received from server',{ serviceTax: ticketSelection.ractive.get('serviceTax'),  totalPrice: ticketSelection.ractive.get('totalPrice') } );
            ticketSelection.ractive.set('stageComplete', true);
            ticketSelection.ractive.set('serviceTax', serviceTax);
            ticketSelection.ractive.set('totalPrice', totalprice);
          }
          else {
            ticketSelection.ractive.set('stageComplete', false);
            ticketSelection.ractive.set('serviceTax', 0);
            ticketSelection.ractive.set('totalPrice', 0);
            ticketSelection.ractive.set('selectedTickets', []);
          }
        });
      }
    });

    ticketSelection.ractive.on('toggle-content', function() {
      if(ticketSelection.ractive.get('visible')) {
        $('.ticket-selection-content').slideUp();
        ticketSelection.ractive.set('visible', false);
      }
      else {
        $('.ticket-selection-content').slideDown();
        ticketSelection.ractive.set('visible', true);
      }
    });

    ticketSelection.ractive.on('activate-discount', function() {
      var discountCode = $('#discountCode').val();
      var ticketsSelected = ticketSelection.ractive.get('selectedTickets');
      if(discountCode && ticketsSelected.length) {
        ticketSelection.ractive.set('discountCodeLoading', true);
        ticketSelection.ractive.set('discountCodeMessage', '');
        console.log('Discount Ticket JSON send to server', { discountCode: discountCode, tickets: ticketsSelected } );
        /*
        $.ajax({
          type: 'POST',
          url: '',
          data: {
            discountCode: discountCode,
            tickets: ticketSelection.ractive.get('selectedTickets')
          },
          dataType: 'json',
          timeout: 5000,
          success: function(data) {
            ticketSelection.ractive.set('discountCodeMessage', data.discountCodeMessage);
            ticketSelection.ractive.set('discountCodeError', false);
            ticketSelection.ractive.set('discountCodeLoading', false);
            ticketSelection.ractive.set('serviceTax', data.serviceTax);
            ticketSelection.ractive.set('totalPrice', data.totalprice);
            
          }
          error: function() {
            ticketSelection.ractive.set('discountCodeMessage', 'Error, try again.');
          }
        }); */

        //stub code
        setTimeout(function() {
          console.log('JSON received from server',{ discountCodeMessage: '10% discount applied successfully', serviceTax: ticketSelection.ractive.get('serviceTax'),  totalPrice: ticketSelection.ractive.get('totalPrice') } );
          ticketSelection.ractive.set('discountCodeError', false);
          ticketSelection.ractive.set('discountCodeLoading', false);
          ticketSelection.ractive.set('discountCodeMessage', '10% discount applied successfully');          
        }, 1000);
      }
      else {
        ticketSelection.ractive.set('discountCodeError', true);
        if(ticketsSelected.length) {
          ticketSelection.ractive.set('discountCodeMessage', 'Please enter a valid code');
        }
        else {
          ticketSelection.ractive.set('discountCodeMessage', 'Please select a ticket');
        }
      }
    });

    ticketSelection.ractive.on('continue', function() {
      if(ticketSelection.ractive.get('stageComplete')) {
        $('.ticket-selection-content').slideUp();
        ticketSelection.ractive.set('visible', false);
        amplify.publish('buyer-details-activate', { serviceTax: ticketSelection.ractive.get('serviceTax'),  totalPrice: ticketSelection.ractive.get('totalPrice'), selectedTickets: ticketSelection.ractive.get('selectedTickets') } );
      }
      else {
        ticketSelection.ractive.set('errorMsg', 'Please select a ticket');
      }
    });
  },
  refresh: function() {
    var ticketSelection = this;
    //Poll to server every 10 seconds
    ticketSelection.requestItemsTimer = setInterval(ticketSelection.ractive.requestItems, 10000)
  }
};

Boxoffice.BuyerDetails = {
  init: function() {
    var buyerDetails = this;

    buyerDetails.ractive = new Ractive ({
      el: 'buyer-details',
      template: '#buyer-details-template',
      data: {
        serviceTax: 0,
        totalPrice: 0,
        totalTickets: [],
        active: false,
        visible: false,
        errorMsg: "",
      },
      oncomplete: function() {

        amplify.subscribe('buyer-details-activate', function(data) {
          buyerDetails.ractive.set('active', true);
          buyerDetails.ractive.set('visible', true);
          var sectionPos = $("#buyer-details").offset().top;
          $('html,body').animate({scrollTop:sectionPos}, '900');
          buyerDetails.ractive.set('serviceTax', data.serviceTax);
          buyerDetails.ractive.set('totalPrice', data.totalPrice);
          var totalTickets = 0;
          data.selectedTickets.forEach(function(obj) {
            totalTickets += obj.qty;
          });
          buyerDetails.ractive.set('totalTickets', totalTickets);
        });
      }
    });

    buyerDetails.ractive.on('toggle-content', function() {
      if(buyerDetails.ractive.get('visible')) {
        $('.buyer-details-content').slideUp();
        buyerDetails.ractive.set('visible', false);
      }
      else {
        $('.buyer-details-content').slideDown();
        buyerDetails.ractive.set('visible', true);
      }
    });

    buyerDetails.ractive.on('continue', function(event) {
      event.original.preventDefault();
      //Cancel TicketSelection.refresh timer
      var formElements = $('#buyer-details-form').serializeArray();
      var formDataValid = true;
      var formData ={};
      for (var formIndex=0; formIndex < formElements.length; formIndex++) {
        if(formElements[formIndex].value === "" || formElements[formIndex].value === "+91") {
            buyerDetails.ractive.set('errorMsg', 'Please fill all fields');
            formDataValid = false;
        }
        formData[formElements[formIndex].name] = formElements[formIndex].value;

      }
      if(formDataValid) {
        buyerDetails.ractive.set('errorMsg', '');
        $('.buyer-details-content').slideUp();
        buyerDetails.ractive.set('visible', false);
        amplify.publish('payment-details-activate');
      }
    });

  }
};

Boxoffice.PaymentDetails = {
  init: function() {
    var paymentDetails = this;

    paymentDetails.ractive = new Ractive ({
      el: 'payment-details',
      template: '#payment-details-template',
      data: {
        active: false,
        visible: false,
        errorMsg: "",
      },
      oncomplete: function() {
        amplify.subscribe('payment-details-activate', function(data) {
          paymentDetails.ractive.set('active', true);
          paymentDetails.ractive.set('visible', true);
          var sectionPos = $("#payment-details").offset().top;
          $('html,body').animate({scrollTop:sectionPos}, '900');
        });
      }
    });

    paymentDetails.ractive.on('toggle-content', function() {
      if(paymentDetails.ractive.get('visible')) {
        $('.payment-details-content').slideUp();
        paymentDetails.ractive.set('visible', false);
      }
      else {
        $('.payment-details-content').slideDown();
        paymentDetails.ractive.set('visible', true);
      }
    });

    paymentDetails.ractive.on('continue', function(event) {
      event.original.preventDefault();
      $('.payment-details-content').slideUp();
      paymentDetails.ractive.set('visible', false);
      amplify.publish('attendee-details-activate');
      return false;
    });
  }
} 

Boxoffice.AttendeeDetails = {
  init: function() {
    var attendeeDetails = this;

    attendeeDetails.ractive = new Ractive ({
      el: 'attendee-details',
      template: '#attendee-details-template',
      data: {
        active: false,
        visible: false,
        errorMsg: "",
        eventName: "",
        attendees: function(qty) {
          var attendees = [];
          for(var attendee = 0; attendee < qty; attendee ++ ) {
            attendees.push(attendee);
          }
          return attendees;
        }
      },
      oncomplete: function() {
        amplify.subscribe('attendee-details-activate', function(data) {
          attendeeDetails.ractive.set('active', true);
          attendeeDetails.ractive.set('visible', true);
          var sectionPos = $("#attendee-details").offset().top;
          $('html,body').animate({scrollTop:sectionPos}, '900');
          attendeeDetails.ractive.set('eventName', window.Boxoffice.Config.event);
        });
      }
    });

    attendeeDetails.ractive.on('toggle-content', function() {
      if(attendeeDetails.ractive.get('visible')) {
        $('.attendee-details-content').slideUp();
        attendeeDetails.ractive.set('visible', false);
      }
      else {
        $('.attendee-details-content').slideDown();
        attendeeDetails.ractive.set('visible', true);
      }
    });
  }
}

$(function() {
  Boxoffice.PaymentProgress.init();
  Boxoffice.TicketSelection.init();
  Boxoffice.TicketSelection.refresh();
  Boxoffice.BuyerDetails.init();
  Boxoffice.PaymentDetails.init();
  Boxoffice.AttendeeDetails.init();
});
