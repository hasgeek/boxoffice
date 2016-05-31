
import {ItemCollectionModel} from '../models/item_collection.js';
import {TableTemplate, AggChartTemplate, ItemCollectionTemplate} from '../templates/item_collection.html.js';

let TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate
});

let AggChartComponent = Ractive.extend({
  template: AggChartTemplate,
  oncomplete: function(){
    let date_item_counts = this.parent.get('date_item_counts');
    const items = this.parent.get('items');
    const date_sales = this.parent.get('date_sales');
    let dates = ['x'];
    let item_counts = {}
    let date_sales_column = ['date_sales']
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

    let bar_graph_headers = columns.map((col) => col[0]).filter((header) => header !== 'x');

    columns.push(date_sales_column);

    this.chart = c3.generate({
      data: {
        x: 'x',
        columns: columns,
        type: 'bar',
        types: {
          date_sales: 'line'
        },
        groups: [
          bar_graph_headers
        ],
        axes: {
          date_sales: 'y2'
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
  }
})

export const ItemCollectionView = {
  init: function(){
    this.ractive = new Ractive({
      el: '#main-content-area',
      template: ItemCollectionTemplate,
      data: {
        title: this.model.get('title'),
        items: this.model.get('items'),
        date_item_counts: this.model.get('date_item_counts'),
        date_sales: this.model.get('date_sales'),
        net_sales: this.model.get('net_sales'),
        sales_delta: this.model.get('sales_delta'),
        today_sales: this.model.get('today_sales')
      },
      components: {TableComponent: TableComponent, AggChartComponent: AggChartComponent}
    });

    this.model.on('change:items', (model, items) => this.ractive.set('items', items));

    this.ractive.on('navigate', function(event, method){
      // kill interval
      clearInterval(this.intervalId);
      eventBus.trigger('navigate', event.context.url);
    });
    window.addEventListener('popstate', (event) => {
      // kill interval
      clearInterval(this.intervalId);
    });
  },
  fetch: function(){
    return this.model.fetch().then(data => {
      this.model.set('title', data.title);
      this.model.set('items', data.items);
      this.model.set('date_item_counts', data.date_item_counts);
      this.model.set('date_sales', data.date_sales);
      this.model.set('net_sales', data.net_sales);
      this.model.set('sales_delta', data.sales_delta);
      this.model.set('today_sales', data.today_sales);
    });
  },
  refresh: function(){
    this.fetch();
  },
  render: function(initData) {
    this.model = new ItemCollectionModel({
      id: initData.id
    });

    this.fetch().then(() => this.init());

    this.intervalId = setInterval(() => this.refresh(), 3000);
  }
}
