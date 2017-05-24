
import {fetch, post, scrollToElement, urlFor, setPageTitle, formatDateTime, Util, updateBrowserHistory} from '../models/util.js';
import {OrderTemplate} from '../templates/admin_order.html.js';
import {SideBarView} from './sidebar.js';

export const OrderView = {
  render: function({ic_id, search, page, size}={}) {
    let url;
    if (search) {
      url = urlFor('search', {
        scope_ns: 'ic',
        scope_id: ic_id,
        resource: 'orders',
        root: true,
        search: search,
        page: page,
        size: size
      });
    } else {
      url = urlFor('index', {
        scope_ns: 'ic',
        scope_id: ic_id,
        resource: 'orders',
        root: true,
        page: page,
        size: size
      });
    }

    const DEFAULT = {
      showOrderSlider: true,
      hideOrderSlider: false,
      showLoader: true,
      hideLoader: false,
      empty: ""
    };

    fetch({
      url: url
    }).done(({org_name, title, orders, total_pages, paginated, current_page}) => {
      // Initial render
      window.orderComponent = new Ractive({
        el: '#main-content-area',
        template: OrderTemplate,
        data:  {
          icTitle: title,
          orders: orders,
          paginated: paginated,
          totalPages: total_pages,
          currentPage: current_page,
          size: 20,
          searchText: search,
          formatDateTime: function (dateTimeString) {
            return formatDateTime(dateTimeString);
          },
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          }
        },
        refresh: function (search='', page='', size='') {
          let url;
          if (search) {
            url = urlFor('search', {
              scope_ns: 'ic',
              scope_id: ic_id,
              resource: 'orders',
              root: true,
              search: search,
              page: page,
              size: size || orderComponent.get('size')
            });
          } else {
            url = urlFor('index', {
              scope_ns: 'ic',
              scope_id: ic_id,
              resource: 'orders',
              root: true,
              page: page,
              size: size || orderComponent.get('size')
            });
          }

          NProgress.start();
          fetch({
            url: url
          }).done((remoteData) => {
            orderComponent.set({
              'orders': remoteData.orders,
              'paginated': remoteData.paginated,
              'totalPages': remoteData.total_pages,
              'currentPage': remoteData.current_page,
              'pages': _.range(1, remoteData.total_pages + 1)
            });
            $('#orders-table').trigger('footable_redraw'); 
            NProgress.done();
            updateBrowserHistory(url);
          });
          scrollToElement("#" + orderComponent.el.id);
        },
        paginate: function (event, page) {
          event.original.preventDefault();
          orderComponent.refresh(this.get('searchText'), page, size);
        },
        clearSearchField: function () {
          orderComponent.set('searchText', DEFAULT.empty);
        },
        showOrder: function (event) {
          // Close opened order sliders
          orderComponent.set('orders.*.show_order', DEFAULT.hideOrderSlider);
          //Show individual order
          orderComponent.set(event.keypath + '.loading', DEFAULT.showLoader);
          NProgress.configure({ showSpinner: false}).start();
          let order_id = event.context.id;
          fetch({
            url: urlFor('view', {
              resource: 'order',
              id: order_id,
              root: true
            })
          }).done((remoteData) => {
            orderComponent.set(event.keypath + '.line_items', remoteData.line_items);
            orderComponent.set(event.keypath + '.show_order', DEFAULT.showOrderSlider);
            NProgress.done();
            orderComponent.set(event.keypath + '.loading', DEFAULT.hideLoader);
            scrollToElement("#" + orderComponent.el.id);
          });
        },
        hideOrder: function (event) {
          orderComponent.set(event.keypath + '.show_order', DEFAULT.hideOrderSlider);
        },
        cancelTicket: function (event) {
          if (window.confirm("Are you sure you want to cancel this ticket?")) {
            orderComponent.set(event.keypath + '.cancel_error', DEFAULT.empty);
            orderComponent.set(event.keypath + '.cancelling', DEFAULT.showLoader);

            post({
              url: event.context.cancel_ticket_url
            }).done(function(response) {
              orderComponent.set(event.keypath + '.cancelled_at', response.result.cancelled_at);
              orderComponent.set(event.keypath + '.cancelling', DEFAULT.hideLoader);
            }).fail(function(response) {
              let error_text;
              if (response.readyState === 4) {
                if (response.status === 500) {
                  error_text = "Server Error";
                }
                else {
                  error_text = JSON.parse(response.responseText).error_description;
                }
              }
              else {
                error_text = "Unable to connect. Please try again later.";
              }
              orderComponent.set(event.keypath + '.cancel_error', error_text);
              orderComponent.set(event.keypath + '.cancelling', DEFAULT.hideLoader);
            });
          }
        },
        oncomplete: function () {
          orderComponent.set('pages', _.range(1, orderComponent.get('totalPages') + 1));

          $('#orders-table').footable({
            breakpoints: {
              phone: 600,
              tablet: 768,
              desktop: 1200,
              largescreen: 1900
            }
          });

          // Close individual order slider (if any) on pressing Escape key
          $('#orders-table').on('keydown', function(e) {
            if (e.which == 27) {
              orderComponent.set('orders.*.show_order', DEFAULT.hideOrderSlider);
              return false;
            }
          });

          var searchTimeout;
          var lastRegisteredSearch = '';
          orderComponent.observe('searchText', function (searchText, prevSearchText) {
            if (searchText !== lastRegisteredSearch) {
              if (searchText.length > 2) {
                window.clearTimeout(searchTimeout);
                lastRegisteredSearch = searchText;
                searchTimeout = window.setTimeout(function(){
                  orderComponent.refresh(searchText);
                }, 1000);
              } else if (searchText.length === 0) {
                orderComponent.refresh();
              }
            }
          });
        }
      });

      SideBarView.render('orders', {org_name, ic_id});
      setPageTitle("Orders", orderComponent.get('icTitle'));
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
