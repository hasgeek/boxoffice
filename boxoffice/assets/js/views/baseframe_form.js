const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');

export const BaseframeForm = Ractive.extend({
  isolated: false,
  template() {
    return this.get('html');
  },
  transitions: { fly },
});

export { BaseframeForm as default };
