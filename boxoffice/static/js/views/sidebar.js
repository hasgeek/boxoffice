import {SideBarModel} from '../models/sidebar.js';
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(ic_config, view) {
    this.on = true;

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sidebarMobileOn: false,
        sideBar: SideBarModel.getItems(ic_config),
        activeItem: view,
        sidebarHide: false
      },
      toggle: function(event) {
        event.original.preventDefault();
        this.set('sidebarMobileOn', !this.get('sidebarMobileOn'));
      },
      navigate: function(event) {
        if(event.context.title !== this.get('activeItem')) {
          NProgress.configure({ showSpinner: false}).start();
          eventBus.trigger('navigate', event.context.url);
        }
      }
    });
  },
  render: function(ic_config, view) {
    if(this.on) {
      this.ractive.set({
        'sideBar': SideBarModel.getItems(ic_config),
        'activeTab': sidebar_item,
        'sidebarHide': false,
        'sidebarMobileOn': false
      });
    }
    else {
      this.init(ic_config, view);
    }
  },
  hide: function() {
    if(this.on) {
      this.ractive.set('sidebarHide', true);
    }
  }
};
