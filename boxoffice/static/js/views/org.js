
import {OrgModel} from '../models/org.js';
// import {renderview} from './renderview.js';
import {orgTemplate} from '../templates/org.html.js';

export const OrgView = {
  render: function(org) {
    OrgModel.fetch({
      url: '/admin/o/' + org.name
    }).then(function(data){
      let ractive = new Ractive({
        el: '#main-content-area',
        // template: '#org-content-template',
        template: orgTemplate,
        data: {
          name: data.name,
          item_collections: data.item_collections
        }
      });

      ractive.on('navigate', function(event, method){
        eventBus.trigger('navigate', event.context.url);
      });
    });
  }
}
