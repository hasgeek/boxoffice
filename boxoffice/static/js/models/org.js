import {fetch} from './util.js';
import {IndexModel} from './index.js';

export const OrgModel = {
  fetch: fetch,
  getUrl: function(org_name, relativeUrl=false){
    if (relativeUrl) {
      return 'o/' + org_name;
    }
    return IndexModel.getUrl() + 'o/' + org_name;
  },
};
