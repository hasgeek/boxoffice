import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const DiscountCouponModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/coupons',
        'relative_path': 'o/' + config.org_name + '/coupons',
        'method': 'GET'
      },
      'view': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/' + config.coupon_id,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
