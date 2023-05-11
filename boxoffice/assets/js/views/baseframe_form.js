const Ractive = require('ractive');

export const BaseframeForm = Ractive.extend({
  isolated: false,
  template() {
    return this.get('html');
  },
});

export { BaseframeForm as default };
