import { Invoice } from './invoice';

const Ractive = require('ractive');

$(() => {
  Ractive.DEBUG = false;
  Invoice.init();
});
