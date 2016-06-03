
import {SideBarModel} from '../models/sidebar.js'
import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarView = {
  init: function(initData) {
    var SideBarView = this;

    this.model = new SideBarModel({
      id: initData.id
    });

    this.ractive = new Ractive({
      el: '#sidebar',
      template: SideBarTemplate,
      data: {
        sideBarView: true,
        sidebarOn: false,
        sideBar: this.model.sideBarItems()
      },
      toggle: function(event) {
        event.original.preventDefault();
        if(this.get('sidebarOn')) {
          this.set('sidebarOn', false);
        }
        else {
          this.set('sidebarOn', true);
        }
      },
      navigate: function(event) {
        NProgress.configure({ showSpinner: false});
        NProgress.start();
        amplify.publish('navigate', {url: event.context.url});
      }
    });

    this.model.on('change:id', function(model, id){
      SideBarView.ractive.set('sideBar', SideBarView.model.sideBarItems());
    });
  },
  render: function(initData) {
    if(this.model) { 
      /* Incase of window.back and window.forward,
      set to new item collection id to update url of sidebar items */      
      if(this.model.get('id') !== initData.id) {
        this.model.set('id', initData.id);
      }
      this.ractive.set('sideBarView', true);
    }
    else {
      this.init(initData);
    }
  },
  hide: function() {
    if(this.model) {
      this.ractive.set('sideBarView', false);
    }
  }
}
