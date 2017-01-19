import {Fetch, Post} from './util.js';
import {IndexModel} from './index.js';

export const ReportModel = {
  fetch: Fetch,
  post: Post,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.icId + '/reports',
        'relativePath': 'ic/' + config.icId + '/reports',
        'method': 'GET'
      },
      'tickets': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.icId + '/reports/tickets.csv',
        'method': 'GET'
      }
    }
    return urls[action];
  }
};
