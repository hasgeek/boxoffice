
import {Util, fetch, urlFor, setPageTitle} from '../models/util.js';
import {TableTemplate, AggChartTemplate, ItemCollectionTemplate} from '../templates/item_collection.html.js';
import {SideBarView} from './sidebar.js'

let TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate
});

let AggChartComponent = Ractive.extend({
  template: AggChartTemplate,
  format_columns: function(){
    let date_item_counts = this.parent.get('date_item_counts');
    const items = this.parent.get('categories').reduce(function (items, category) {
      return items.concat(category.items);
    }, []);
    const date_sales = this.parent.get('date_sales');
    let dates = ['x'];
    let item_counts = {}
    let date_sales_column = ['sales']
    for (let item_date in date_item_counts) {
      dates.push(item_date);
      date_sales_column.push(date_sales[item_date]);
      items.forEach((item) => {
        if (!item_counts[item.id]) {
          item_counts[item.id] = [];
        }
        if (date_item_counts[item_date].hasOwnProperty(item.id)) {
          // If an item has been bought on this item_date
          item_counts[item.id].push(date_item_counts[item_date][item.id]);
        } else {
          // Item not bought on this date
          item_counts[item.id].push(0);
        }
      })
    }

    let columns = [dates];
    items.forEach((item) =>{
      columns.push([item.title].concat(item_counts[item.id]));
    })

    // let bar_graph_headers = columns.map((col) => col[0]).filter((header) => header !== 'x');

    columns.push(date_sales_column);
    return columns;
  },
  oncomplete: function(){
    let columns = this.format_columns();
    let bar_graph_headers = _.without(_.map(columns, _.first), 'x', 'sales')

    this.chart = c3.generate({
      data: {
        x: 'x',
        columns: this.format_columns(),
        type: 'bar',
        types: {
          sales: 'line'
        },
        groups: [
          bar_graph_headers
        ],
        axes: {
          sales: 'y2'
        }
      },
      bar: {
        width: {
          ratio: 0.5 // this makes bar width 50% of length between ticks
        }
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: {
            format: '%d-%m'
          },
          label: 'Date'
        },
        y: {
          label: 'No. of tickets'
        },
        y2: {
          show: true,
          label: 'Sales'
        }
      }
    });

    this.parent.on('data_update', () => {
      this.chart.load({
        columns: this.format_columns()
      });
    });

  }
})

export const ItemCollectionView = {
  render: function ({ic_id}={}) {

    fetch({
      url: urlFor('view', {resource: 'ic', id: ic_id, root: true})
    }).done(({org_name, title, categories, date_item_counts, date_sales, today_sales, net_sales, sales_delta}) => {
      // Initial render
      let icComponent = new Ractive({
        el: '#main-content-area',
        template: ItemCollectionTemplate,
        data: {
          icTitle: title,
          categories: categories,
          date_item_counts: date_item_counts,
          date_sales: date_sales,
          net_sales: net_sales,
          sales_delta: sales_delta,
          today_sales: today_sales,
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          }
        },
        components: {TableComponent: TableComponent, AggChartComponent: AggChartComponent}
      });

      SideBarView.render('dashboard', {org_name, ic_id});
      setPageTitle(icComponent.get('icTitle'));
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
}
