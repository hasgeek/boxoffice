import {fetch} from './util.js';

export const IndexModel = {
  fetch: fetch,
  urlFor: function(action){
    let urls = {
      'index': {
        'path': Backbone.history.root,
        'relative_path': '/',
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
