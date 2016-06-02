import {SideBarTemplate} from '../templates/sidebar.html.js';

export const SideBarComponent = Ractive.extend({
  isolated: false,
  sidebarOn: false,
  template: SideBarTemplate,
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
    this.parent.navigate(event.context.url);
  }
});