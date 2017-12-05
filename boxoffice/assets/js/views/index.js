
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
var Ractive = require('ractive');
import {fetch, urlFor, setPageTitle} from '../models/util.js';
import {IndexModel} from '../models/index.js';
import {IndexTemplate} from '../templates/index.html.js';
import {SideBarView} from './sidebar.js'

export const IndexView = {
  render: function() {

    fetch({
      url: urlFor('index', {root: true})
    }).then(function({orgs}){
      let indexComponent = new Ractive({
        el: '#main-content-area',
        template: IndexTemplate,
        data: {
          orgs: orgs
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
