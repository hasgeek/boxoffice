import { eventBus } from './navigate';
import { SideBarModel } from '../models/sidebar';
import { SideBarTemplate } from '../templates/sidebar.html';

const Ractive = require('ractive');
const NProgress = require('nprogress');

export const SideBarView = {
  init(view, menuConfig) {
    this.on = true;

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sidebarMobileOn: false,
        sidebarItems: SideBarModel.getItems(menuConfig),
        activeItem: view,
        sidebarHide: false,
      },
      toggle(event) {
        event.original.preventDefault();
        this.set('sidebarMobileOn', !this.get('sidebarMobileOn'));
      },
      navigate(event) {
        if (event.context.view !== this.get('activeItem')) {
          NProgress.configure({ showSpinner: false }).start();
          eventBus.trigger('navigate', event.context.url);
        }
      },
    });
  },
  render(view, menuConfig) {
    if (this.on) {
      this.ractive.set({
        sidebarItems: SideBarModel.getItems(menuConfig),
        activeItem: view,
        sidebarHide: false,
        sidebarMobileOn: false,
      });
    } else {
      this.init(view, menuConfig);
    }
  },
  hide() {
    if (this.on) {
      this.ractive.set('sidebarHide', true);
    }
  },
};

export { SideBarView as default };
