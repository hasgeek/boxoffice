
window._ = require("underscore");
window.Backbone = require("backbone");
window.d3 = require("d3");
window.c3 = require("c3");
window.Clipboard = require("clipboard");
window.daterangepicker = require("bootstrap-daterangepicker");
window.moment = require("moment");

import {Router} from './router';

$(function(){
  let appRouter = new Router();
  Backbone.history.start({pushState: true, root: appRouter.url_root});
  window.eventBus = _.clone(Backbone.Events);
  window.eventBus.on('navigate', function (msg) {
    appRouter.navigate(msg, {trigger: true});
  })
});
