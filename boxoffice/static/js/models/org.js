import {fetch, urlFor} from './util.js';
import {IndexModel} from './index.js';

export const OrgModel = {
  fetch: fetch,
  urlFor: function(view, action, {org_name}={}){
    let urls = urlFor(view, {org_name});
    urls['view-items'] = {
      'path': `${urls['index']['path']}/items`,
      'method': 'GET'
    }
    return urls[action];
  }
};
