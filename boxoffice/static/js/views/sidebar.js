import {SideBarModel} from '../models/sidebar.js';
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(view, ic_config) {
    this.on = true;

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sidebarMobileOn: false,
        sidebarItems: SideBarModel.getItems(ic_config),
        activeItem: view,
        sidebarHide: false
      },
      toggle: function(event) {
        event.original.preventDefault();
        this.set('sidebarMobileOn', !this.get('sidebarMobileOn'));
      },
      navigate: function(event) {
        console.log('navigate');
        console.log(event.context.url);
        console.log(event.context.view);
        console.log(this.get('activeItem'));
        console.log(this);
        if (event.context.view !== this.get('activeItem')) {
          NProgress.configure({ showSpinner: false}).start();
          console.log('before trigger');
          eventBus.trigger('navigate', event.context.url);
          console.log('after trigger');
        }
      }
    });
  },
  render: function(view, ic_config) {
    if (this.on) {
      this.ractive.set({
        'sidebarItems': SideBarModel.getItems(ic_config),
        'activeItem': view,
        'sidebarHide': false,
        'sidebarMobileOn': false
      });
    }
    else {
      this.init(view, ic_config);
    }
  },
  hide: function() {
    if (this.on) {
      this.ractive.set('sidebarHide', true);
    }
  }
};
