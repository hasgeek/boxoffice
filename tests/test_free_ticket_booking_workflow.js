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

casper.test.begin("Boxoffice UI test for free ticket booking workflow", 13, function suite(test) {

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
  casper.wait(120000, function() {
    test.assertExist('.buyer-form-title', "Buyer form exists");
    this.fill('form.buyer-details', {
        'name':    'HasGeek',
        'email':    'testing@hasgeek.com',
        'phone':   '+919900011234'
    }, false);
    // this.capture('boxoffice_test3_stage2.png');
    test.assertExist('.summary', 'Booking Summary exists');
    test.assertExist('.discount-applied', 'Discount policy exist in booking summary');
    this.click('#stage2-proceed', "Checkout button exist");
  });

  casper.waitForSelector('.confirmation-icon', function() {
    test.assertExist('div.confirmation-msg', "Ticket booking confirmation message exists");
    test.assertExist('#view-ticket', "View ticket button exist");
    test.assertExist('#view-ticket', "View cash receipt button exist");
    // this.capture('boxoffice_test3_stage3.png');
  });

  casper.run(function() {
    test.done();
  });
});