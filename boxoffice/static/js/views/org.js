
import {fetch, urlFor, setPageTitle} from '../models/util.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function({org_name}={}) {
    fetch({
      url: urlFor('view', {resource: 'o', id: org_name, root: true})
    }).then(function({id, org_title, item_collections}){
      let orgComponent = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          orgName: org_name,
          orgTitle: org_title,
          item_collections: item_collections
        }
      });

      SideBarView.render('org', {org_name, org_title});
      setPageTitle(org_title);
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
