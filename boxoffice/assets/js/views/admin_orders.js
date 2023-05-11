/* eslint-disable no-unused-vars */
import {
  Util,
  fetch,
  post,
  scrollToElement,
  urlFor,
  setPageTitle,
} from '../models/util';
import { OrdersTemplate } from '../templates/admin_orders.html';
import { SideBarView } from './sidebar';

const NProgress = require('nprogress');
const Ractive = require('ractive');

export const OrdersView = {
  render({ menuId } = {}) {
    fetch({
      url: urlFor('index', {
        scope_ns: 'menu',
        scope_id: menuId,
        resource: 'orders',
        root: true,
      }),
    }).done(
      ({
        account_name: accountName,
        account_title: accountTitle,
        menu_title: menuTitle,
        orders,
      }) => {
        // Initial render
        const orderComponent = new Ractive({
          el: '#main-content-area',
          template: OrdersTemplate,
          data: {
            accountName,
            menuId,
            menuTitle,
            orders,
            formatDateTime(dateTimeString) {
              return Util.formatDateTime(dateTimeString);
            },
            formatToIndianRupee(amount) {
              return Util.formatToIndianRupee(amount);
            },
          },
        });

        SideBarView.render('orders', {
          accountName,
          accountTitle,
          menuId,
          menuTitle,
        });
        setPageTitle('Orders', menuTitle);
        NProgress.done();

        $('#orders-table').footable({
          breakpoints: {
            phone: 600,
            tablet: 768,
            desktop: 1200,
            largescreen: 1900,
          },
        });

        $('#orders-table').on('footable_filtering', (e) => {
          const selected = $('#filter-status').find(':selected').val();
          if (selected && selected.length > 0) {
            e.filter +=
              e.filter && e.filter.length > 0 ? ` ${selected}` : selected;
            e.clear = !e.filter;
          }
        });

        $('#filter-status').change((e) => {
          e.preventDefault();
          $('#orders-table').trigger('footable_filter', {
            filter: $('#filter').val(),
          });
        });

        $('#search-form').on('keydown', (e) => {
          if (e.key === 'Enter') {
            return false;
          }
          return true;
        });

        $('#orders-table').on('keydown', (e) => {
          if (e.key === 'Escape') {
            orderComponent.set('orders.*.show_order', false);
            return false;
          }
          return true;
        });

        window.addEventListener('popstate', (event) => {
          NProgress.configure({ showSpinner: false }).start();
        });
      }
    );
  },
};

export { OrdersView as default };
