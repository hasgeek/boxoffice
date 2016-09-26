import {fetch, post, convertFormToJSON} from './util.js';
import {IndexModel} from './index.js';

export const DiscountPolicyModel = {
  fetch: fetch,
  post: post,
  convertFormToJSON: convertFormToJSON,
  urlFor: function(action, config){
    let base_url = IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/discount_policies';
    let urls = {
      'index': {
        'path': config.page ? base_url + '?page=' + config.page : base_url,
        'relative_path': 'o/' + config.org_name + '/discount_policies',
        'method': 'GET'
      },
      'search': {
        'path': config.page ? base_url + '?search=' + config.search + '?page=' + config.page : base_url + '?search=' + config.search,
        'method': 'GET'
      },
      'new': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/discount_policy/new',
        'method': 'POST'
      },
      'edit': {
        'path': IndexModel.urlFor('index')['path'] + 'discount_policy/' + config.discount_policy_id + '/edit',
        'method': 'POST'
      },
      'generate_coupon': {
        'path': IndexModel.urlFor('index')['path'] + 'discount_policy/' + config.discount_policy_id + '/generate_coupon',
        'method': 'POST'
      },
      'list_coupons': {
        'path': IndexModel.urlFor('index')['path'] + 'discount_policy/' + config.discount_policy_id + '/coupons',
        'method': 'POST'
      },
    }
    return urls[action];
  }
};
