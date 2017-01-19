import {Fetch, Post} from './util.js';
import {IndexModel} from './index.js';

export const OrderModel = {
  fetch: Fetch,
  post: Post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.icId + '/orders',
        'relativePath': 'ic/' + config.icId + '/orders',
        'method': 'GET'
      },
      'view': {
        'path': IndexModel.urlFor('index')['path'] + 'order/' + config.orderId,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
