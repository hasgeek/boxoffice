
import {OrgModel} from '../models/org.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function(org) {

    OrgModel.fetch({
      url: OrgModel.urlFor('index', {orgName: org.name})['path']
    }).then(function(data){
      let orgComponent = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          title: data.title,
          itemCollections: data.item_collections
        }
      });

      SideBarView.hide();

      NProgress.done();

      orgComponent.on('navigate', function(event, method){
        NProgress.configure({ showSpinner: false}).start();
        eventBus.trigger('navigate', event.context.url);
      });
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false}).start();
    });
  }
}
