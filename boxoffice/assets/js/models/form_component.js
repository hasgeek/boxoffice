var Ractive = require('ractive');
import {Util} from './util.js';

export const BaseframeForm = Ractive.extend({
  isolated: false,
  template: function(data) {
    return this.get('formTemplate');
  },
  computed: {
    formId: {
      get: function() {
        if(this.get('formTemplate')) {
          return Util.getElementId(this.get('formTemplate'));
        }
      }
    }
  }
});
