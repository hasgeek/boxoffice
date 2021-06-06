var Ractive = require('ractive');

export const BaseframeForm = Ractive.extend({
  isolated: false,
  template: function () {
    return this.get('html');
  },
});
