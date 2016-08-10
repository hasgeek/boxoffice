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
      'view': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/' + config.discount_policy_id,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
