
import {OrgModel} from '../models/org.js';
// import {renderview} from './renderview.js';
import {orgTemplate} from '../templates/org.html.js';

export const OrgView = {
  render: function(org) {
    this.orgModel = new OrgModel({
      name: org.name
    });
    this.orgModel.fetch().then(function(data){
      this.ractive = new Ractive({
        el: '#main-content-area',
        // template: '#org-content-template',
        template: orgTemplate,
        data: {
          name: data.name,
          item_collections: data.item_collections
        }
      });
      NProgress.done();
      this.ractive.on('navigate', function(event, method){
        NProgress.configure({ showSpinner: false});
        NProgress.start();
        eventBus.trigger('navigate', event.context.url);
      });
    });

  }
}
