import {fetch, post, urlFor} from './util.js';
import {IndexModel} from './index.js';

export const OrderModel = {
  fetch: fetch,
  post: post,
  urlFor: function (view, action, {ic_id, order_id}={}) {
    let urls = urlFor(view, {ic_id});
    urls['view-order'] = {
      'path': `${urls['index']['path']}/${order_id}`,
      'method': 'GET'
    }
    return urls[action];
  }
};
