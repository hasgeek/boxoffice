import {fetch, post, urlFor} from './util.js';
import {IndexModel} from './index.js';

export const ReportModel = {
  fetch: fetch,
  post: post,
  urlFor: function (view, action, {ic_id}={}) {
    let urls = urlFor(view, {ic_id});
    urls['tickets'] = {
      'path': `${urls['index']['path']}/tickets.csv`,
      'method': 'GET'
    }
    return urls[action];
  }
};
