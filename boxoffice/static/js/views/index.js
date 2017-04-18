
import {setPageTitle} from '../models/util.js';
import {IndexModel} from '../models/index.js';
import {IndexTemplate} from '../templates/index.html.js';
import {SideBarView} from './sidebar.js'

export const IndexView = {
  render: function() {

    IndexModel.fetch({
      url: IndexModel.urlFor('index')['path']
    }).then(function(data){
      let indexComponent = new Ractive({
        el: '#main-content-area',
        template: IndexTemplate,
        data: {
          orgs: data.orgs
        }
      });

      SideBarView.hide();
      setPageTitle("Admin");
      NProgress.done();

      indexComponent.on('navigate', function(event, method){
        NProgress.configure({ showSpinner: false}).start();
        eventBus.trigger('navigate', event.context.url);
      });
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false}).start();
    });
  }
}
