
var Ractive = require("ractive");
Ractive.transitions.fly = require( 'ractive-transitions-fly' );
var FormValidator = require('validate-js');

import {Invoice} from './invoice';

$(function() {
  Ractive.DEBUG = false;
  Invoice.init();
});
