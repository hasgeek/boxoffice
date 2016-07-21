import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const OrderModel = {
  fetch: fetch,
  post: post,
  getUrl: function(ic_id, relativeUrl=false){
    if (relativeUrl) {
      return '/ic/' + ic_id + '/orders';
    }
    return IndexModel.url_root + '/ic/' + ic_id + '/orders';
  }
};
