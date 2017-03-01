
import {Util, fetch, scrollToElement, updateBrowserHistory, urlFor} from '../models/util.js';
import {ItemTemplate} from '../templates/admin_item.html.js';
import {SideBarView} from './sidebar.js';

export const ItemView = {
  render: function (view, {ic_id, search, page}={}) {
    let url;
    if (search) {
      url = urlFor('search', {
        scope_ns: 'ic',
        scope_id: ic_id,
        resource: 'items',
        root: true,
        search: search,
        page: page
      });
    } else {
      url = urlFor('index', {
        scope_ns: 'ic',
        scope_id: ic_id,
        resource: 'items',
        root: true,
        page: page
      });
    }

    const DEFAULT = {
      empty: ""
    };

    fetch({
      url: url
    }).done(({title, items, total_pages, paginated, current_page}) => {
      // Initial render
      let itemComponent = new Ractive({
        el: '#main-content-area',
        template: ItemTemplate,
        data:  {
          title: title,
          items: items,
          paginated: paginated,
          totalPages: total_pages,
          currentPage: current_page,
          searchText: search,
          formatCurrency: function (currency) {
            return Util.formatToIndianRupee(currency);
          }
        },
        refresh: function (search='', page='') {
          let url;
          if (search) {
            url = urlFor('search', {
              scope_ns: 'ic',
              scope_id: ic_id,
              resource: 'items',
              root: true,
              search: search,
              page: page
            });
          } else {
            url = urlFor('index', {
              scope_ns: 'ic',
              scope_id: ic_id,
              resource: 'items',
              root: true,
              page: page
            });
          }

          NProgress.start();
          fetch({
            url: url
          }).done((remoteData) => {
            itemComponent.set({
              'items': remoteData.items,
              'paginated': remoteData.paginated,
              'totalPages': remoteData.total_pages,
              'currentPage': remoteData.current_page,
              'pages': _.range(1, remoteData.total_pages + 1)
            });
            NProgress.done();
            updateBrowserHistory(window.location.href, url);
          });
          scrollToElement("#" + itemComponent.el.id);
        },
        paginate: function (event, page) {
          event.original.preventDefault();
          itemComponent.refresh(DEFAULT.empty, page);
        },
        clearSearchField: function () {
          itemComponent.set('searchText', DEFAULT.empty);
        },
        oncomplete: function () {

          itemComponent.observe('searchText', function (searchText, prevSearchText) {
            if (searchText.length > 2) {
              itemComponent.refresh(searchText);
            } else if (searchText.length === 0 && prevSearchText) {
              itemComponent.refresh();
            }
          });

          itemComponent.set('pages', _.range(1, itemComponent.get('totalPages') + 1));

        }
      });

      SideBarView.render('items', {ic_id});

      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
