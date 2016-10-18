import {fetch} from './util.js';
import {IndexModel} from './index.js';

export const OrgModel = {
  fetch: fetch,
  urlFor: function(action, {org_name}={}){
    let urls = {
      'index': {
        'path': `${IndexModel.urlFor('index')['path']}o/${org_name}`,
        'relative_path': `o/${org_name}`,
        'method': 'GET'
      },
      'view_items': {
        'path': `${IndexModel.urlFor('index')['path']}o/${org_name}/items`,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
