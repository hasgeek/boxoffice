
window._ = require("underscore");
window.Backbone = require("backbone");
window.d3 = require("d3");
window.c3 = require("c3");

import {Router} from './router';

$(function(){
  let appRouter = new Router();
  Backbone.history.start({pushState: true, root: appRouter.url_root});
  window.eventBus = _.clone(Backbone.Events);
  window.eventBus.on('navigate', function(msg){
    appRouter.navigate(msg, {trigger: true});
  })
  window.admin = {};
  /* Title tag in Baseframe template is defined as "pageTitle — siteTitle"
  Split the page title to get the site title and assign it to window.admin.siteTitle
  eg:- The page title is "JSFoo 2017 — Boxoffice", splits into ["JSFoo 2016", Boxoffice"]
  where the last item is the site title */
  window.admin.siteTitle = (function () {
	  let currentPageTitle = $('title').html();
	  let subTitles = currentPageTitle.split(' — ');
	  return subTitles[subTitles.length-1];
	})();
});
