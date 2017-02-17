import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const ReportModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, {ic_id}={}){
    let base_url = `${IndexModel.urlFor('index')['path']}ic/${ic_id}/reports`
    let urls = {
      'index': {
        'path': base_url,
        'relative_path': `ic/${ic_id}/reports`,
        'method': 'GET'
      },
      'tickets': {
        'path': `${base_url}/tickets.csv`,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
