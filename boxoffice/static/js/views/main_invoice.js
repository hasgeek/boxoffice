
window.Ractive = require("ractive");
window.Ractive.transitions.fly = require( 'ractive-transitions-fly' );
window.FormValidator = require('validate-js');

import {Invoice} from './invoice';

$(function() {
  Ractive.DEBUG = false;

  Invoice.init();

});
