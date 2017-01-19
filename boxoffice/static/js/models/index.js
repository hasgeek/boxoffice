import {Fetch} from './util.js';

export const IndexModel = {
  fetch: Fetch,
  urlFor: function(action){
    let urls = {
      'index': {
        'path': Backbone.history.root,
        'relativePath': '/',
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
