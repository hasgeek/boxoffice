import {SideBarModel} from '../models/sidebar.js';
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(view, icConfig) {
    this.on = true;

    this.component = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sidebarMobileOn: false,
        sidebarItems: SideBarModel.getItems(icConfig),
        activeItem: view,
        sidebarHide: false
      },
      toggle: function(event) {
        event.original.preventDefault();
        this.set('sidebarMobileOn', !this.get('sidebarMobileOn'));
      },
      navigate: function(event) {
        if (event.context.view !== this.get('activeItem')) {
          NProgress.configure({ showSpinner: false}).start();
          eventBus.trigger('navigate', event.context.url);
        }
      }
    });
  },
  render: function(view, icConfig) {
    if (this.on) {
      this.component.set({
        'sidebarItems': SideBarModel.getItems(icConfig),
        'activeItem': view,
        'sidebarHide': false,
        'sidebarMobileOn': false
      });
    }
    else {
      this.init(view, icConfig);
    }
  },
  hide: function() {
    if (this.on) {
      this.component.set('sidebarHide', true);
    }
  }
};
