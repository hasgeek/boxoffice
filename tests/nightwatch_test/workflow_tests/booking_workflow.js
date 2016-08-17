module.exports = {
  'Ticket booking' : function (client) {
    var ticket_total;
    client
      .url(client.globals.url)
      .waitForElementVisible('body', client.globals.delay)
      .waitForElementVisible('div.boxoffice-section', client.globals.delay)
      .assert.visible('div#conference-ticket p.ticket-title')
      //Add conference ticket to cart
      .click('div#conference-ticket button.increment')
      .waitForElementVisible('div#conference-ticket p.subtotal', client.globals.delay)
      .getText("div#conference-ticket p.subtotal span", function(subtotal) {
        ticket_total = subtotal.value;
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
