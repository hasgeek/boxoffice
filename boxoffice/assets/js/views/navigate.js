const Backbone = require('backbone');
const _ = require('underscore');
const NProgress = require('nprogress');

export const eventBus = _.clone(Backbone.Events);

export function navigateTo(url) {
  NProgress.configure({ showSpinner: false }).start();
  // Relative paths(without '/admin') are defined in router.js
  eventBus.trigger('navigate', url.replace('/admin', ''));
  // Scroll to top of the page
  window.scrollTo(0, 0);
}
