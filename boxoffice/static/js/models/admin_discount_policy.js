import {fetch, post, getFormParameters, urlFor} from './util.js';
import {IndexModel} from './index.js';

export const DiscountPolicyModel = {
  fetch: fetch,
  post: post,
  getFormParameters: getFormParameters,
  urlFor: function (view, action, {org_name, search, page, discount_policy_id}={}) {
    let urls = urlFor(view, {org_name});
    let baseUrl = urls['index']['path'];
    urls['index']['path'] = page ? `${baseUrl}?page=${page}` : baseUrl;
    let additionalUrls = {
      'search': {
        'path': page ? `${baseUrl}?search=${search}&page=${page}` : `${baseUrl}?search=${search}`,
        'method': 'GET'
      },
      'edit': {
        'path': `${baseUrl}/${discount_policy_id}/edit`,
        'method': 'POST'
      },
      'generate_coupon': {
        'path': `${baseUrl}/${discount_policy_id}/generate_coupon`,
        'method': 'POST'
      },
      'list_coupons': {
        'path': `${baseUrl}/${discount_policy_id}/coupons`,
        'method': 'POST'
      }
    }
    _.extend(urls, additionalUrls);
    return urls[action];
  }
};
