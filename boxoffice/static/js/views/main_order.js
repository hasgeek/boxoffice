
window.Ractive = require("ractive");
window.Ractive.transitions.fly = require( 'ractive-transitions-fly' );
window.FormValidator = require('validate-js');

import {Order} from './order';

$(function() {
  Ractive.DEBUG = false;

  Order.init();

});
