import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const DiscountPolicyModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/discount_policies',
        'relative_path': 'o/' + config.org_name + '/discount_policies',
        'method': 'GET'
      },
      'new': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/discount_policies/new',
        'method': 'POST'
      },
      'edit': {
        'path': IndexModel.urlFor('index')['path'] + config.discount_policy_id + '/edit',
        'method': 'POST'
      },
      'generate_coupon': {
        'path': IndexModel.urlFor('index')['path'] + config.discount_policy_id + '/coupon',
        'method': 'POST'
      },
    }
    return urls[action];
  }
};
