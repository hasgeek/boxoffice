import { Order } from './order';

const Ractive = require('ractive');
Ractive.transitions.fly = require('ractive-transitions-fly');

$(() => {
  Ractive.DEBUG = false;

  Order.init();
});
