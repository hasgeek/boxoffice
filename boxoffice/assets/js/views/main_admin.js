
var _ = require("underscore");
var NProgress = require('nprogress');
var Backbone = require("backbone");
import {Router} from './router';
import {FormView} from './form_view.js';

let appRouter = new Router();
Backbone.history.start({pushState: true, root: appRouter.url_root});

export const eventBus = _.clone(Backbone.Events);

export const navigateTo = function(url){
  NProgress.configure({ showSpinner: false}).start();
  //Relative paths(without '/admin') are defined in router.js
  eventBus.trigger('navigate', url.replace('/admin', ''));
}

function handleNavigation(){
  /*
    To trigger page transitions through pushState, add `data-navigate` to
    the anchor tag and specify the URL in the `href` attribute
  */
  document.addEventListener('click', function(event){
    event.preventDefault();
    var ele = event.target;
    if ('navigate' in ele.dataset){
      navigateTo(ele.getAttribute('href'));
    }
  });

  eventBus.on('navigate', function (msg) {
    // Set `boxofficeFirstLoad` to `false` since this is this isn't the first loaded page anymore
    if (!window.boxofficeFirstLoad){
      window.boxofficeFirstLoad = false;
    }
    FormView.hide();
    appRouter.navigate(msg, {trigger: true});
  });
}

$(function(){
  handleNavigation();  
});
