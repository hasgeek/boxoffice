import {fetch, post, getFormParameters, scrollToElement} from './util.js';
import {IndexModel} from './index.js';

export const DiscountPolicyModel = {
  fetch: fetch,
  post: post,
  getFormParameters: getFormParameters,
  scrollToElement: scrollToElement,
  urlFor: function(action, {org_name, search, page, discount_policy_id}={}){
    let base_url = `${IndexModel.urlFor('index')['path']}o/${org_name}/discount_policy`;
    let urls = {
      'index': {
        'path': page ? `${base_url}?page=${page}` : base_url,
        'relative_path': `o/${org_name}/discount_policy`,
        'method': 'GET'
      },
      'search': {
        'path': page ? `${base_url}?search=${search}&page=${page}` : `${base_url}?search=${search}`,
        'method': 'GET'
      },
      'new': {
        'path': `${IndexModel.urlFor('index')['path']}o/${org_name}/discount_policy/new`,
        'method': 'POST'
      },
      'edit': {
        'path': `${IndexModel.urlFor('index')['path']}discount_policy/${discount_policy_id}/edit`,
        'method': 'POST'
      },
      'generate_coupon': {
        'path': `${IndexModel.urlFor('index')['path']}discount_policy/${discount_policy_id}/generate_coupon`,
        'method': 'POST'
      },
      'list_coupons': {
        'path': `${IndexModel.urlFor('index')['path']}discount_policy/${discount_policy_id}/coupons`,
        'method': 'POST'
      },
      'lookup': {
        'path': `${IndexModel.urlFor('index')['path']}discount_policy`,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
