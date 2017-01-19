import {Fetch} from './util.js';
import {IndexModel} from './index.js';

export const OrgModel = {
  fetch: Fetch,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'o/' + config.orgName,
        'relativePath': 'o/' + config.orgName,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
