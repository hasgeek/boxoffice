
var _ = require("underscore");
var NProgress = require('nprogress');
var Backbone = require("backbone");
import {Router} from './router';
export const eventBus = _.clone(Backbone.Events);

export const navigateTo = function(url){
	NProgress.configure({ showSpinner: false}).start();
	//Relative paths(without '/admin') are defined in router.js
	eventBus.trigger('navigate', url.replace('/admin', ''));
}

export const navigateBack = function(){
  window.history.go(-1);
  return false;
}

$(function(){
  let appRouter = new Router();
  Backbone.history.start({pushState: true, root: appRouter.url_root});

  document.addEventListener('click', function(event){
    event.preventDefault();
    var ele = event.target;
    if ('navigate' in ele.dataset){
      navigateTo(ele.getAttribute('href'));
    }
  });

  eventBus.on('navigate', function (msg) {
    appRouter.navigate(msg, {trigger: true});
  })
});
