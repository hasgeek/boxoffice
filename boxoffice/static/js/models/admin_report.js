import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const ReportModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, {ic_id}={}){
    let urls = {
      'index': {
        'path': `${IndexModel.urlFor('index')['path']}ic/${ic_id}/reports`,
        'relative_path': `ic/${ic_id}/reports`,
        'method': 'GET'
      },
      'tickets': {
        'path': `${IndexModel.urlFor('index')['path']}ic/${ic_id}/reports/tickets.csv`,
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
