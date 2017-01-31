var system = require('system');

casper.options.waitTimeout = 120000;
casper.options.stepTimeout = 120000;

var host = "http://testing.travis.dev:8000?code=coupon2"; //presumably 127.0.0.1
var items = {
  'conference': {
    'conference-ticket': {
      'add': 1,
      'subtract': 0,
      'discount': '₹3,500',
      'subtotal': '₹0'
    }
  }
};
var finalAmount = '₹0';

casper.test.begin("Boxoffice UI test for free ticket booking workflow", 16, function suite(test) {

  casper.start(host, function() {
    test.assertHttpStatus(200, "Ticketing page loaded");
  });
  
  //Booking workflow stage 1 - Selecting tickets
  casper.waitForSelector('div.ticket-selection-content', function() {
    this.echo("Boxoffice widget is visible");
  });

  casper.waitForSelector('.discount-price', function() {
    test.assertEquals(casper.fetchText('#conference #conference-ticket .discount-price'), items['conference']['conference-ticket']['subtotal'], "Discounted price exists is correct");
    this.click('#conference #conference-ticket .increment');
  });

  casper.waitForSelector('.discount-amount', function() {
    test.assertEquals(casper.fetchText('#conference #conference-ticket .discount-amount span'), items['conference']['conference-ticket']['discount'],  '#conference #conference-ticket discount exists and is correct');
    test.assertEquals(casper.fetchText('#conference #conference-ticket .subtotal span'), items['conference']['conference-ticket']['subtotal'], '#conference #conference-ticket subtotal exists and is correct');
    test.assertExists('#conference #conference-ticket .applied', "Discount policy exists");
  });

  casper.waitWhileSelector('.loader', function() {
    test.assertEquals(casper.fetchText('span.final-amount'), finalAmount, "Final amount exist and is correct");
    test.assertExist('#stage1-proceed', "Continue button exists");
    // this.capture('boxoffice_test3_stage1.png');
    this.click('#stage1-proceed');
  });

  //Booking workflow stage 2 - Filling buyer details
  casper.waitForSelector('.buyer-form-title', function() {
    test.assertExist('.buyer-form-title', "Buyer form exists");
    this.fill('form.buyer-details', {
        'name':    'HasGeek',
        'email':    'testing@hasgeek.com',
        'phone':   '+919900011234'
    }, false);
    // this.capture('boxoffice_test3_stage2.png');
    test.assertExist('.summary', 'Booking Summary exists');
    test.assertExist('.discount-applied', 'Discount policy exist in booking summary');
    test.assertExist('#stage2-proceed', 'Checkout button exist');
    this.click('#stage2-proceed');
  });

  casper.waitForSelector('.confirmation-icon', function() {
    test.assertExist('div.confirmation-msg', "Ticket booking confirmation message exists");
    test.assertExist('#view-ticket', "View ticket button exist");
    test.assertExist('#view-receipt', "View cash receipt button exist");
    // this.capture('boxoffice_test3_stage3.png');
    var ticket_url = casper.getElementAttribute('#view-ticket', 'href');
    casper.thenOpen(ticket_url, function() {
      this.echo(this.getTitle());
      casper.waitForSelector('.ticket', function() {
        test.assertExist('.fill-details', "Fill attendee details button exists");
        this.click('.fill-details');
        casper.wait(6000, function() {
          this.fill('form.assignee-form', {
              'fullname':    'HasGeek',
              'email':    'testing@hasgeek.com',
              'phone':   '+919900011234'
          }, false);
          this.click('.assign-ticket');
          casper.wait(6000, function() {
            test.assertExist('.confirmation-msg', "Ticket assignment confirmation exists");
          });
        });
      });
    });
  });

  casper.run(function() {
    test.done();
  });
});