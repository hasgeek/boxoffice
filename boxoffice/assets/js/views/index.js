/* eslint-disable no-unused-vars */
import { eventBus } from './navigate';
import { fetch, urlFor, setPageTitle } from '../models/util';
import { IndexTemplate } from '../templates/index.html';
import { SideBarView } from './sidebar';

const NProgress = require('nprogress');
const Ractive = require('ractive');

export const IndexView = {
  render() {
    fetch({
      url: urlFor('index', { root: true }),
    }).then(({ orgs }) => {
      const indexComponent = new Ractive({
        el: '#main-content-area',
        template: IndexTemplate,
        data: {
          orgs,
        },
      });

      SideBarView.hide();
      setPageTitle('Admin');
      NProgress.done();

      indexComponent.on('navigate', (event, method) => {
        NProgress.configure({ showSpinner: false }).start();
        eventBus.trigger('navigate', event.context.url);
      });
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false }).start();
    });
  },
};

export { IndexView as default };
