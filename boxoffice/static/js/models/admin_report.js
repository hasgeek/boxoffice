import {fetch, post} from './util.js';
import {IndexModel} from './index.js';

export const ReportModel = {
  fetch: fetch,
  post: post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.ic_id + '/reports',
        'relative_path': 'ic/' + config.ic_id + '/reports',
        'method': 'GET'
      },
      'tickets': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.ic_id + '/reports/tickets.csv',
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
