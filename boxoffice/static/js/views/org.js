
import {OrgModel} from '../models/org.js';
// import {renderview} from './renderview.js';
import {orgTemplate} from '../templates/org.html.js';

export const OrgView = {
  render: function(org) {
    if (!this.orgModel) {
      this.orgModel = new OrgModel({
        name: org.name
      });
    }
    this.orgModel.fetch().then(function(data){
      if (!this.ractive) {
        this.ractive = new Ractive({
          el: '#main-content-area',
          // template: '#org-content-template',
          template: orgTemplate,
          data: {
            name: data.name,
            item_collections: data.item_collections
          }
        });
        this.ractive.on('navigate', function(event, method){
          // console.log(event.context.url);
          eventBus.trigger('navigate', event.context.url);
        });

      } else {
        this.ractive.render();
      }
    });

  }
}
