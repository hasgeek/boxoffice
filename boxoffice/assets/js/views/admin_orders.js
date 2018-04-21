
var NProgress = require('nprogress');
var Ractive = require('ractive');
import {Util, fetch, post, scrollToElement, urlFor, setPageTitle} from '../models/util.js';
import {OrdersTemplate} from '../templates/admin_orders.html.js';
import {SideBarView} from './sidebar.js';

export const OrdersView = {
  render: function({ic_id}={}) {
    fetch({
      url: urlFor('index', {scope_ns: 'ic', scope_id: ic_id, resource: 'orders', root: true})
    }).done(({org_name, org_title, ic_title, orders}) => {
      // Initial render
      let orderComponent = new Ractive({
        el: '#main-content-area',
        template: OrdersTemplate,
        data:  {
          orgName: org_name,
          icId: ic_id,
          icTitle: ic_title,
          orders: orders,
          formatDateTime: function (dateTimeString) {
            return Util.formatDateTime(dateTimeString);
          },
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          }
        }
      });

      SideBarView.render('orders', {org_name, org_title, ic_id, ic_title});
      setPageTitle("Orders", ic_title);
      NProgress.done();

      $('#orders-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200,
          largescreen: 1900
        }
      });

      $('#orders-table').on('footable_filtering', function (e) {
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

      $("#search-form").on("keypress", function(e) {
        if (e.which == 13) {
          return false;
        }
      });

      $("#orders-table").on("keydown", function(e) {
        if (e.which == 27) {
          orderComponent.set('orders.*.show_order', false);
          return false;
        }
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
