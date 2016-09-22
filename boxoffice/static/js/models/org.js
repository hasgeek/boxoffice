import {fetch} from './util.js';
import {IndexModel} from './index.js';

export const OrgModel = {
  fetch: fetch,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name,
        'relative_path': 'o/' + config.org_name,
        'method': 'GET'
      },
      'view_items': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.org_name + '/items',
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
