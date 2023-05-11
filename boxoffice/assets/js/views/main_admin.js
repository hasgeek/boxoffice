import { Router } from './router';
import { FormView } from './form_view';
import { eventBus, navigateTo } from './navigate';

const Backbone = require('backbone');

const appRouter = new Router();
Backbone.history.start({ pushState: true, root: appRouter.url_root });

function handleNavigation() {
  /*
    To trigger page transitions through pushState, add `data-navigate` to
    the anchor tag and specify the URL in the `href` attribute
  */
  document.addEventListener('click', (event) => {
    const ele = event.target;
    if ('navigate' in ele.dataset) {
      event.preventDefault();
      navigateTo(ele.getAttribute('href'));
    }
  });

  eventBus.on('navigate', (msg) => {
    // Set `boxofficeFirstLoad` to `false` since this is this isn't the first loaded page anymore
    if (window.boxofficeFirstLoad) {
      window.boxofficeFirstLoad = false;
    }
    FormView.hide();
    appRouter.navigate(msg, { trigger: true });
  });
}

$(() => {
  handleNavigation();
});
