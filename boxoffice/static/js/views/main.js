
window._ = require("underscore");
window.Backbone = require("backbone");
window.d3 = require("d3");
window.c3 = require("c3");

import {Router} from './router';

$(function(){
  let appRouter = new Router();
  Backbone.history.start({pushState: true, root: "/admin/"});
  window.eventBus = _.clone(Backbone.Events);
  window.eventBus.on('navigate', function(msg){
    appRouter.navigate(msg, {trigger: true});
  })
});
