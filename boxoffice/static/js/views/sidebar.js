import {SideBarModel} from '../models/sidebar.js'
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(initData) {
    this.id = initData.id;

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sideBarView: true,
        sidebarOn: false,
        sideBar: SideBarModel.items(initData.id)
      },
      toggle: function(event) {
        event.original.preventDefault();
        this.set('sidebarOn', !this.get('sidebarOn'));
      },
      navigate: function(event) {
        NProgress.configure({ showSpinner: false});
        NProgress.start();
        eventBus.trigger('navigate', event.context.url);
      }
    });
  },
  render: function(initData) {
    if(this.id) { 
      /* Incase of window.back and window.forward,
      set to new item collection id to update url of sidebar items */      
      if(this.id !== initData.id) {
        this.ractive.set('sideBar', SideBarModel.items(initData.id));
      }
      this.ractive.set('sideBarView', true);
    }
    else {
      this.init(initData);
    }
  },
  hide: function() {
    if(this.id) {
      this.ractive.set('sideBarView', false);
    }
  }
}
