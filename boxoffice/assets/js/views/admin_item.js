
import {fetch, urlFor, setPageTitle} from '../models/util.js';
import {ItemTemplate} from '../templates/admin_item.html.js';
import {SideBarView} from './sidebar.js';

export const ItemView = {
  render: function({org_name}={}) {
    fetch({
      url: urlFor('new', {resource: 'items', scope_ns: 'o', scope_id: org_name, root: true})
    }).done(({form_html}) => {
      // Initial render
      let reportComponent = new Ractive({
        el: '#main-content-area',
        template: ItemTemplate,
        data:  {
          formHTML: "form_html",
        }
      });

    //   SideBarView.render('items', {org_name});
      setPageTitle("New item");
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
