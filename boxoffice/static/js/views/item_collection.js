
import {ItemCollectionModel} from '../models/item_collection.js';
import {TableTemplate, AggChartTemplate, ItemCollectionTemplate} from '../templates/item_collection.html.js';
import {SideBarView} from './sidebar.js'

let TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate
});

let AggChartComponent = Ractive.extend({
  template: AggChartTemplate,
  formatColumns: function(){
    let dateItemCounts = this.parent.get('dateItemCounts');
    const items = this.parent.get('items');
    const dateSales = this.parent.get('dateSales');
    let dates = ['x'];
    let itemCounts = {};
    let dateSalesColumn = ['sales'];
    for (let itemDate in dateItemCounts) {
      dates.push(itemDate);
      dateSalesColumn.push(dateSales[itemDate]);
      items.forEach((item) => {
        if (!itemCounts[item.id]) {
          itemCounts[item.id] = [];
        }
        if (dateItemCounts[itemDate].hasOwnProperty(item.id)) {
          // If an item has been bought on this item_date
          itemCounts[item.id].push(dateItemCounts[itemDate][item.id]);
        } else {
          // Item not bought on this date
          itemCounts[item.id].push(0);
        }
      })
    }

    let columns = [dates];
    items.forEach((item) =>{
      columns.push([item.title].concat(itemCounts[item.id]));
    })

    // let bar_graph_headers = columns.map((col) => col[0]).filter((header) => header !== 'x');

    columns.push(dateSalesColumn);
    return columns;
  },
  oncomplete: function(){
    let columns = this.formatColumns();
    let barGraphHeaders = _.without(_.map(columns, _.first), 'x', 'sales')

    this.chart = c3.generate({
      data: {
        x: 'x',
        columns: this.formatColumns(),
        type: 'bar',
        types: {
          sales: 'line'
        },
        groups: [
          barGraphHeaders
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
        columns: this.formatColumns()
      });
    });

  }
})

export const ItemCollectionView = {
  render: function(config) {

    ItemCollectionModel.fetch({
      url: ItemCollectionModel.urlFor('index', {icId: config.id})['path']
    }).done((remoteData) => {
      // Initial render
      let icComponent = new Ractive({
        el: '#main-content-area',
        template: ItemCollectionTemplate,
        data: ItemCollectionModel.formatData(remoteData),
        components: {TableComponent: TableComponent, AggChartComponent: AggChartComponent}
      });

      NProgress.done();

      SideBarView.render('dashboard', {'orgName': remoteData.org_name, 'icId': config.id});

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
}
