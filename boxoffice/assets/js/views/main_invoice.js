import { Invoice } from './invoice';

const Ractive = require('ractive');
Ractive.transitions.fly = require('ractive-transitions-fly');

$(() => {
  Ractive.DEBUG = false;
  Invoice.init();
});
