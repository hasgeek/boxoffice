import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const OrderModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.getUrl() + 'ic/' + config.ic_id + '/orders',
        'relative_path': 'ic/' + config.ic_id + '/orders',
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
