
import {OrgModel} from '../models/org.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function(org) {

    OrgModel.fetch({
      url: OrgModel.getUrl(org.name)
    }).then(function(data){
      let ractive = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          title: data.title,
          item_collections: data.item_collections
        }
      });

      SideBarView.hide();

      NProgress.done();

      ractive.on('navigate', function(event, method){
        NProgress.configure({ showSpinner: false}).start();
        eventBus.trigger('navigate', event.context.url);
      });
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false}).start();
    });
  }
}
