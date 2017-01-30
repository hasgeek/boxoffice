var system = require('system');

casper.options.waitTimeout = 120000;
casper.options.stepTimeout = 120000;


var host = "http://testing.travis.dev:8000"; //presumably 127.0.0.1
var items = {
  'conference': {
    'conference-ticket': {
      'add': 2,
      'subtract': 1,
      'discount': false,
      'subtotal': true
    },
    'single-day': {
      'add': 3,
      'subtract': 6,
      'discount': false,
      'subtotal': false
    },
  },
  'merchandise': {
    't-shirt': {
      'add': 6,
      'subtract': 1,
      'discount': true,
      'subtotal': true
    }
  }
};


casper.test.begin("Boxoffice UI test for ticket booking workflow", 17, function suite(test) {

  casper.start(host, function() {
    test.assertHttpStatus(200, "Ticketing page loaded");
  });
  
  //Booking workflow stage 1 - Selecting tickets
  casper.waitForSelector('div.ticket-selection-content', function() {
    this.echo("Boxoffice widget is visible");
    for (var itemCategory in items) {
      for (item in items[itemCategory]) {
        var add = items[itemCategory][item]['add'] || 0;
        var subtract = items[itemCategory][item]['subtract'] || 0;

        for (var i = 0; i < add; i++) {
          this.click('#' + itemCategory + ' #' + item + ' .increment');
        }

        for (var i = 0; i < subtract; i++) {
          this.click('#' + itemCategory + ' #' + item + ' .decrement');
        }
      }
    }
  });

  casper.wait(120000, function() {
    for (var itemCategory in items) {
      for (item in items[itemCategory]) {
        
        if (items[itemCategory][item]['discount']) {
          test.assertExists('#' + itemCategory + ' #' + item + ' .discount-amount span', '#' + itemCategory + ' #' + item + ' discount exists');
        } 
        else {
          test.assertDoesntExist('#' + itemCategory + ' #' + item + ' .discount-amount span', '#' + itemCategory + ' #' + item + ' discount doesn\'t exist');
        }

        if (items[itemCategory][item]['subtotal']) {
          test.assertExists('#' + itemCategory + ' #' + item + ' .subtotal span', '#' + itemCategory + ' #' + item + ' subtotal exists');
        } else {
          test.assertDoesntExist('#' + itemCategory + ' #' + item + ' .subtotal span', '#' + itemCategory + ' #' + item + ' subtotal doesn\'t exist');
        }

      }
    }
  });

  casper.waitWhileSelector('.loader', function() {
    test.assertExist('span.final-amount', "Final amount exists");
    test.assertExist('#stage1-proceed', "Continue button exists");
    // this.capture('boxoffice_test1_stage1.png');
    this.click('#stage1-proceed');
  });

  //Booking workflow stage 2 - Filling buyer details
  casper.waitWhileSelector('.ticket-selection-content', function() {
    test.assertExist('.buyer-form-title', "Buyer form exists");
    this.click('.edit-order');
    test.assertExist('div.ticket-selection-content', "Edit order takes back to ticket selection");
    this.click('#stage1-proceed');
  });

  casper.waitWhileSelector('.ticket-selection-content', function() {
    this.fill('form.buyer-details', {
        'name':    'HasGeek',
        'email':    'testing@hasgeek.com',
        'phone':   '+919900011234'
    }, false);
    // this.capture('boxoffice_test1_stage2.png');
    test.assertExist('.summary', 'Booking Summary exists');
    this.click('#stage2-proceed', "Checkout button exist");
  });

  casper.wait(120000, function() {
    casper.withFrame(0, function() {
      test.assertExist('div#payment-options', "Razorpay checkout window exists");
      this.click('div.payment-option');
      casper.wait(casper.options.waitTimeout, function() {
        this.sendKeys('#card_number', "4111111111111111");
        this.sendKeys('#card_expiry', "11/99");
        this.sendKeys('#card_cvv', "123");
        test.assertExist('#footer', "Razorpay pay button exist");
        this.click('#footer');
      });
    });
  });

  casper.wait(120000, function() {
    casper.withPopup(/razorpay/, function() {
      this.click('.success');
    });
  });

  casper.wait(120000, function() {
    this.capture('boxoffice_test1_stage3.png');
    test.assertExist('div.confirmation-msg', "Ticket booking confirmation message exists");
    test.assertExist('#view-ticket', "View ticket button exist");
    test.assertExist('#view-ticket', "View cash receipt button exist");
  });

  casper.run(function() {
    test.done();
  });
});
