
import {OrgModel} from '../models/org.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function(view, {org_name}={}) {

    OrgModel.fetch({
      url: OrgModel.urlFor(view, 'index', {org_name})['path']
    }).then(function({id, name, title, item_collections}){
      let ractive = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          title: title,
          item_collections: item_collections
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
