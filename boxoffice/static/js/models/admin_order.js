import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const OrderModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.ic_id + '/orders',
        'relative_path': 'ic/' + config.ic_id + '/orders',
        'method': 'GET'
      },
      'view_order': {
        'path': IndexModel.urlFor('index')['path'] + 'order/' + config.order_id,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
