import {SideBarModel} from '../models/sidebar.js';
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(sidebar_item, org, ic) {
    this.on = true;

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sidebarMobileOn: false,
        sideBar: SideBarModel.getItems(org, ic),
        activeItem: sidebar_item,
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
  render: function(sidebar_item="", org="", ic="") {
    if(this.on) {
      this.ractive.set({
        'sideBar': SideBarModel.getItems(org, ic),
        'activeTab': sidebar_item,
        'sidebarHide': false,
        'sidebarMobileOn': false
      });
    }
    else {
      this.init(sidebar_item, org, ic);
    }
  },
  hide: function() {
    if(this.on) {
      this.ractive.set('sidebarHide', true);
    }
  }
};
