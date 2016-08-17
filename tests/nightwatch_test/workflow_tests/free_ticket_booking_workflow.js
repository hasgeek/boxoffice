module.exports = {
  'Free ticket booking' : function (client) {
    client
      .url(client.globals.couponUrl)
      .waitForElementVisible('body', client.globals.delay)
      .waitForElementVisible('div.boxoffice-section', client.globals.delay)
      .assert.visible('div#conference-ticket p.ticket-title')
      //Add conference ticket to cart
      .click('div#conference-ticket button.increment')
      .waitForElementVisible('div#conference-ticket p.subtotal', client.globals.delay)
      .getText('div#conference-ticket p.subtotal span', function(subtotal) {
        this.assert.equal(subtotal.value, '0')
      })
      .moveToElement('div.ticket-total', 10, 10)
      .assert.visible('div.proceed-button-wrapper button#stage1-proceed')
      .click('div.proceed-button-wrapper button#stage1-proceed')
      .waitForElementVisible('p.buyer-form', client.globals.delay)
      .setValue('input[name=name]', client.globals.userName)
      .setValue('input[name=email]', client.globals.userEmail)
      .setValue('input[name=phone]', client.globals.userPhone)
      .getText('.final-amount', function(finalAmount) {
        this.assert.equal(finalAmount.value, '0')
      })
      .moveToElement('p.summary', 10, 10)
      .assert.visible('div.proceed-button-wrapper button[type=submit]')
      .click('div.proceed-button-wrapper button[type=submit]')
      .pause(client.globals.delay)
      .waitForElementVisible('div.confirmation-msg', client.globals.delay)
      .click('a.receipt-button:nth-child(1)')
      .click('a.receipt-button:nth-child(2)')
  },
  after : function(client) {
    client.end();
  }
};

