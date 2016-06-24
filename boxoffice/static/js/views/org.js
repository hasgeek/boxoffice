
import {OrgModel} from '../models/org.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function(org) {
    SideBarView.hide();

    OrgModel.fetch({
      url: '/admin/o/' + org.name
    }).then(function(data){
      let ractive = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          name: data.name,
          item_collections: data.item_collections
        }
      });

      NProgress.done();

      ractive.on('navigate', function(event, method){
        eventBus.trigger('navigate', event.context.url);
      });
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false});
      NProgress.start();
    });
  }
}
