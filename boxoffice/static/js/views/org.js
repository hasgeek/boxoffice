
import {OrgModel} from '../models/org.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function(org) {
    this.orgModel = new OrgModel({
      name: org.name
    });

    SideBarView.hide();

    this.orgModel.fetch().then(function(data){
      this.ractive = new Ractive({
        el: '#main-content-area',
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

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false});
      NProgress.start();
    });
  }
}
