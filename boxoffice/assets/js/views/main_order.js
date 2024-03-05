import { Order } from './order';

const Ractive = require('ractive');

$(() => {
  Ractive.DEBUG = false;

  Order.init();
});
