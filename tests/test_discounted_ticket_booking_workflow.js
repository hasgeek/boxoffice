var system = require('system');

casper.options.waitTimeout = 120000;
casper.options.stepTimeout = 60000;

var host = "http://testing.travis.dev:8000?code=forever"; //presumably 127.0.0.1
var items = {
  'conference': {
    'conference-ticket': {
      'add': 1,
      'subtract': 0,
      'discount': '₹100',
      'subtotal': '₹3,400'
    }
  }
};
var finalAmount = '₹3,400';

casper.test.begin("Boxoffice UI test for discounted ticket booking workflow", 12, function suite(test) {

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
    // this.capture('boxoffice_test2_stage1.png');
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
    // this.capture('boxoffice_test2_stage2.png');
    test.assertExist('.summary', 'Booking Summary exists');
    test.assertExist('.discount-applied', 'Discount policy exist in booking summary');
    test.assertExist('#stage2-proceed', 'Checkout button exist');
    this.click('#stage2-proceed');
  });

  casper.wait(120000, function() {
    casper.withFrame(0, function() {
      test.assertExist('div#payment-options', "Razorpay checkout window exists");
      this.click('div.payment-option');
      casper.wait(5000, function() {
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
    test.assertExist('#view-receipt', "View cash receipt button exist");
  });

  casper.run(function() {
    test.done();
  });
});