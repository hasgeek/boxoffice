module.exports = {
  'Discounted tickets booking' : function (client) {
    var ticket_price;
    var ticket_total;
    client
      .url(client.globals.couponCodeUrl)
      .waitForElementVisible('body', client.globals.delay)
      .waitForElementVisible('div.boxoffice-section', client.globals.delay)
      .assert.visible('div#conference-ticket p.ticket-title')
      .assert.visible('div#conference-ticket p.discount-price')
      .getText("div#conference-ticket p.ticket-price.strike", function(price) {
        ticket_price = price.value
      })
      .getText("div#conference-ticket p.discount-price", function(discount_price) {
        this.assert.equal(discount_price.value, 0.85 * ticket_price)
      })
      //Add conference ticket to cart
      .click('div#conference-ticket button.increment')
      .waitForElementVisible('div#conference-ticket p.subtotal', client.globals.delay)
      .getText("div#conference-ticket p.subtotal span", function(subtotal) {
        ticket_total = parseInt(subtotal.value, 10);
        //15% discount
        this.assert.equal(subtotal.value, 0.85 * ticket_price)
      })
      .assert.visible('div#single-day p.ticket-title')
      .getText("div#single-day p.ticket-price", function(price) {
        ticket_price = price.value
      })
      //Add single day ticket to cart
      .click('div#single-day button.increment')
      .waitForElementVisible('div#single-day p.subtotal', client.globals.delay)
      .getText("div#single-day p.subtotal span", function(subtotal) {
        ticket_total += parseInt(subtotal.value, 10);
        this.assert.equal(subtotal.value, ticket_price)
      })
      .assert.visible('div#t-shirt p.ticket-title')
      .getText("div#t-shirt p.ticket-price", function(price) {
        ticket_price = price.value
      })
      .perform(function(done){
        for(var i=0; i<5; i++) {
          //Add 5 t-shirts to cart
          client.click('div#t-shirt button.increment')
        }
        done();
      })
      .waitForElementVisible('div#t-shirt p.subtotal', client.globals.delay)
      .getText("div#t-shirt p.subtotal span", function(subtotal) {
        ticket_total += parseInt(subtotal.value, 10);
        //5% discount on 5 tickets
        this.assert.equal(subtotal.value, 0.95 * ticket_price * 5)
      })
      .waitForElementVisible('div.ticket-total span', client.globals.delay)
      .getText("div.ticket-total span", function(total_amount) {
        this.assert.equal(total_amount.value, ticket_total)
      })
      .assert.visible('div.proceed-button-wrapper button#stage1-proceed')
      .click('div.proceed-button-wrapper button#stage1-proceed')
      .waitForElementVisible('p.buyer-form', client.globals.delay)
      .setValue('input[name=name]', client.globals.userName)
      .setValue('input[name=email]', client.globals.userEmail)
      .setValue('input[name=phone]', client.globals.userPhone)
      .getText('.final-amount', function(final_amount) {
        this.assert.equal(final_amount.value, ticket_total)
      })
      .perform(function(done){
        console.log("Final order amount", ticket_total);
        done();
      })
      .assert.visible('div.proceed-button-wrapper button[type=submit]')
      .click('div.proceed-button-wrapper button[type=submit]')
      .waitForElementVisible('div.razorpay-container', client.globals.delay)
      .frame(0)
      .waitForElementVisible('div#payment-options', client.globals.delay)
      .click('div.payment-option')
      .pause(client.globals.delay)
      .setValue('input#card_number', client.globals.cardNo)
      .setValue('input#card_expiry', client.globals.cardExpiry)
      .setValue('input#card_cvv', client.globals.cardCvv)
      .click('button#footer')
      .pause(client.globals.delay)
      .window_handles(function(result) {
        var temp = result.value[1];
        this.switchWindow(temp);
      })
      .waitForElementVisible('input.success', client.globals.delay)
      .click('input.success')
      .pause(client.globals.delay)
      .window_handles(function(result) {
        var temp = result.value[0];
        this.switchWindow(temp);
      })
      .waitForElementVisible('div.confirmation-msg', client.globals.delay)
      .click('a.receipt-button:nth-child(1)')
      .click('a.receipt-button:nth-child(2)')
  },
  after : function(client) {
    client.end();
  }
};
