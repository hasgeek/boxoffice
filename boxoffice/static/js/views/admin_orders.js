
import {OrdersModel} from '../models/admin_orders.js';
import {OrdersTemplate} from '../templates/admin_orders.html.js';
import {SideBarView} from './sidebar.js';

export const OrdersView = {
  render: function(config) {
    let url = `/admin/ic/${config.id}/orders`;
    OrdersModel.fetch({
      url: url
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: OrdersTemplate,
        data:  {
          title: remoteData.title,
          orders: remoteData.orders
        }
      });

      SideBarView.render('orders', {'org_name': remoteData.org_name, 'ic_id': config.id});

      NProgress.done();

      $('#orders-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1400
        }
      });

      $('#orders-table').bind('footable_filtering', function (e) {
        let selected = $('#filter-status').find(':selected').val();
        if (selected && selected.length > 0) {
          e.filter += (e.filter && e.filter.length > 0) ? ' ' + selected : selected;
          e.clear = !e.filter;
        }
      });

      $('#filter-status').change(function (e) {
        e.preventDefault();
        $('#orders-table').trigger('footable_filter', {filter: $('#filter').val()});
      });

      main_ractive.on('navigate', function(event, method){
        //View each order
        NProgress.configure({ showSpinner: false}).start();
        eventBus.trigger('navigate', event.context.url);
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
