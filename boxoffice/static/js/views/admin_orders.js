
import {OrdersModel} from '../models/admin_orders.js';
import {OrdersTemplate} from '../templates/admin_orders.html.js';
import {TableSearch} from '../models/util.js';

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
        data: remoteData
      });

      $('#orders-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200
        }
      });

      let tableSearch = new TableSearch('orders-table');
      $('#main-content input#search').keyup(function(e){
        $('#orders-table tbody tr.footable-detail-show').addClass('hidden');
        let hits = tableSearch.searchRows($(this).val());
        $(hits.join(",")).removeClass('hidden');
      });

      // Setup polling
      let intervalId = setInterval(() => {
        OrdersModel.fetch({
          url: url
        }).done((freshData) => {
          main_ractive.set(freshData);
           //force a redraw
          $('#orders-table').trigger('footable_redraw');
        });
      }, 30000);

      main_ractive.on('navigate', function(event, method){
        // kill interval
        clearInterval(intervalId);
        eventBus.trigger('navigate', event.context.url);
      });

      window.addEventListener('popstate', (event) => {
        // kill interval
        clearInterval(intervalId);
      });
    });
  }
}
