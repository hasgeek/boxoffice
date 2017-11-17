
var _ = require("underscore");
var Backbone = require("backbone");
import {Router} from './router';
export const eventBus = _.clone(Backbone.Events);

$(function(){
  let appRouter = new Router();
  Backbone.history.start({pushState: true, root: appRouter.url_root});
  eventBus.on('navigate', function (msg) {
    appRouter.navigate(msg, {trigger: true});
  })
});
