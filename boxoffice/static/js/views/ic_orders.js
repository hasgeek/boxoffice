
import {OrdersModel} from '../models/orders.js';
import {OrdersTableTemplate, OrdersTemplate} from '../templates/orders.html.js';
import {SideBarView} from './sidebar.js'

export const OrdersView = {
  init: function(){
    var ordersView = this;

    this.ractive = new Ractive({
      el: '#main-content-area',
      template: OrdersTemplate,
      data: {
        title: this.model.get('title'),
        orders: this.model.get('orders'),
        fileUrl: this.model.fileUrl()
      }
    });

    NProgress.done();

    this.model.on('change:orders', function(model, orders){
      ordersView.ractive.set('orders', orders);
    });

    amplify.subscribe('navigate', function(navigate) {
      // kill interval
      clearInterval(ordersView.intervalId);
      eventBus.trigger('navigate', navigate.url);
    });

    window.addEventListener('popstate', (event) => {
      // kill interval
      clearInterval(this.intervalId);
      NProgress.configure({ showSpinner: false});
      NProgress.start();
    });
  },
  fetch: function(){
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

    SideBarView.render({id: this.model.get('id')});

    this.fetch().then(() => this.init());

    this.intervalId = setInterval(() => this.refresh(), 3000);
  }
}
