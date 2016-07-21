import {fetch} from './util.js';

export const IndexModel = {
  fetch: fetch,
  getUrl: function() {
    return Backbone.history.root;
  }
};
