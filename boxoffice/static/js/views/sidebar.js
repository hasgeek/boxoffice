import {SideBarModel} from '../models/sidebar.js'
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(org, ic) {
    this.on = true;

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sidebarMobileOn: false,
        sideBar: SideBarModel.items(org, ic)
      },
      toggle: function(event) {
        event.original.preventDefault();
        this.set('sidebarMobileOn', !this.get('sidebarMobileOn'));
      },
      navigate: function(event) {
        NProgress.configure({ showSpinner: false}).start();
        eventBus.trigger('stop-refresh');
        eventBus.trigger('navigate', event.context.url);
      }
    });
  },
  render: function(org="", ic="") {
    if(this.on) {
      this.ractive.set('sideBar', SideBarModel.items(org, ic));
    }
    else {
      this.init(org, ic);
    }
  }
}
