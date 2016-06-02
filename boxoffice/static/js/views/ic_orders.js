
import {OrdersModel} from '../models/orders.js';
import {SideBarModel} from '../models/sidebar.js'
import {OrdersTableTemplate, OrdersTemplate} from '../templates/orders.html.js';
import {SideBarComponent} from './sidebar.js'

export const OrdersView = {
  init: function(){

    this.ractive = new Ractive({
      el: '#main-content-area',
      template: OrdersTemplate,
      data: {
        title: this.model.get('title'),
        sideBar: this.model.get('sidebar'),
        orders: this.model.get('orders'),
      },
      components: {SideBarComponent: SideBarComponent},
      navigate: function(url) {
        // kill interval
        clearInterval(this.intervalId);
        eventBus.trigger('navigate', url);
      }
    });

    this.model.on('change:orders', function(model, orders){
      this.ractive.set('orders', orders);
    });

    window.addEventListener('popstate', (event) => {
      // kill interval
      clearInterval(this.intervalId);
    });
  },
  fetch: function(){
    var sidebar = new SideBarModel();
    this.model.set('sidebar', sidebar.sideBarItems(this.model.get('id')));

    return this.model.fetch().then(data => {
      this.model.set('title', data.title);
      this.model.set('orders', data.orders);
    });
  },
  refresh: function(){
    this.fetch();
  },
  render: function(initData) {
    this.model = new OrdersModel({
      id: initData.id
    });

    this.fetch().then(() => this.init());

    NProgress.done();

    this.intervalId = setInterval(() => this.refresh(), 3000);
  }
}
