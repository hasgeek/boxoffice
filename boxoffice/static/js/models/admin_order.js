import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const OrderModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, {ic_id, order_id}={}){
    let urls = {
      'index': {
        'path': `${IndexModel.urlFor('index')['path']}ic/${ic_id}/orders`,
        'relative_path': `ic/${ic_id}/orders`,
        'method': 'GET'
      },
      'view': {
        'path': `${IndexModel.urlFor('index')['path']}order/${order_id}`,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
