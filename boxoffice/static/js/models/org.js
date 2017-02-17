import {fetch} from './util.js';
import {IndexModel} from './index.js';

export const OrgModel = {
  fetch: fetch,
  urlFor: function(action, {org_name}={}){
    let base_url = `${IndexModel.urlFor('index')['path']}o/${org_name}`
    let urls = {
      'index': {
        'path': base_url,
        'relative_path': `o/${org_name}`,
        'method': 'GET'
      },
      'view_items': {
        'path': `${base_url}/items`,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
