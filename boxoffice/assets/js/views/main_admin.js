
var _ = require("underscore");
var NProgress = require('nprogress');
var Backbone = require("backbone");
import {Router} from './router';
export const eventBus = _.clone(Backbone.Events);

$(function(){
  let appRouter = new Router();
  Backbone.history.start({pushState: true, root: appRouter.url_root});

  document.addEventListener('click', function(event){
    event.preventDefault();
    var ele = event.target;
    console.log(ele.href);
    if ('navigate' in ele.dataset){
      NProgress.configure({ showSpinner: false}).start();
      //Relative paths(without '/admin') are defined in router.js
      eventBus.trigger('navigate', ele.getAttribute('href').replace('/admin', ''));
    }
  });

  eventBus.on('navigate', function (msg) {
    appRouter.navigate(msg, {trigger: true});
  })
});
