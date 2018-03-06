
var Ractive = require("ractive");
var NProgress = require('nprogress');
var _ = require("underscore");
var c3 = require("c3");
import {eventBus} from './main_admin.js'
import {Util, fetch, urlFor, setPageTitle} from '../models/util.js';
import {SideBarView} from './sidebar.js'

export const TableTemplate = `
  <div class="col-xs-12">
    <div class="table-responsive item-stats-table">
      <table class="table table-bordered table-hover stats-table">
        <thead>
          <tr class="info">
            <th>Category</th>
            <th>#</th>
            <th>Ticket</th>
            <th>Available</th>
            <th>Sold</th>
            <th>Free</th>
            <th>Cancelled</th>
            <th>Current Price</th>
            <th>Net Sales</th>
          </tr>
        </thead>
        <tbody>
          {{#categories}}{{# { category: . } }}
            {{#category.items:index}}
              <tr>
                {{#if !index}}
                  <td class="active" rowspan="{{category.items.length}}">{{ category.title }}</td>
                {{/if}}
                <td>{{ index + 1 }}</td>
                <td><a class="" href="/admin/item/{{id}}" data-navigate>{{ title }}</a></td>
                <td>{{ quantity_available }}</td>
                <td>{{ sold_count }} <input type="checkbox" name="sold" on-click="onItemsSelected(event, 'sold_count')" /></td>
                <td>{{ free_count }} <input type="checkbox" name="free" on-click="onItemsSelected(event, 'free_count')" /></td>
                <td>{{ cancelled_count }}</td>
                {{#if active_price}}
                  <td>{{ formatToIndianRupee(active_price) }}</td>
                {{else}}
                  <td>No active price</td>
                {{/if}}
                <td>{{ formatToIndianRupee(net_sales) }}</td>
              </tr>
            {{/category.items}}
          {{/}}{{/categories}}
          <tr>
            <td></td>
            <td class="active" colspan="3">Tickets booked</td>
            <td class="active text-center" colspan="2">{{ totalSelected }}</td>
            <td colspan="4"></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
`

export const AggChartTemplate = `
  <div class="chart-wrapper card">
    <div id="chart" class="sales-chart">
    </div>
  </div>
`

export const ItemCollectionTemplate = `
  <div class="content-wrapper clearfix">
    <h1 class="header col-xs-12">{{ icTitle }}</h1>
    <div class="title-wrapper col-xs-12">
      <a class="boxoffice-button boxoffice-button-action btn-right" href="/admin/ic/{{ic_id}}/item/new" data-navigate>
        New item
      </a>
      <a class="boxoffice-button boxoffice-button-action btn-right btn-margin-right" href="/admin/ic/{{ic_id}}/category/new" data-navigate>
        New category
      </a>
      <a class="boxoffice-button boxoffice-button-action btn-right btn-margin-right" href="/admin/ic/{{ic_id}}/edit" data-navigate>
        Edit item collection
      </a>
      <a class="boxoffice-button boxoffice-button-action btn-right btn-margin-right" href="/{{ org_name }}/{{ ic_name }}">
        View listing
      </a>
    </div>
    <div class="stats clearfix">
      <div class="col-md-4 col-sm-6 col-xs-12">
        <div class="card clearfix">
          <div class="card-left">
            <p class="card-left-content"><i class="fa fa-plus"></i></p>
          </div>
          <div class="card-right">
            <h3 class="card-right-content">Net sales</h3>
            <p class="card-right-content">{{ formatToIndianRupee(net_sales) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 col-sm-6 col-xs-12">
        <div class="card clearfix">
          <div class="card-left">
            <p class="card-left-content"><i class="fa fa-calendar-o"></i></p>
          </div>
          <div class="card-right">
            <h3 class="card-right-content">Today's sales</h3>
            <p class="card-right-content">{{ formatToIndianRupee(today_sales) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 col-sm-6 col-xs-12">
        <div class="card clearfix">
          <div class="card-left">
            {{#if sales_delta > 0 }}
              <p class="card-left-content"><i class="fa fa-arrow-up"></i></p>
            {{elseif sales_delta < 0 }}
              <p class="card-left-content"><i class="fa fa-arrow-down"></i></p>
            {{else}}
              <p class="card-left-content"><i class="fa fa-minus"></i></p>
            {{/if}}
          </div>
          <div class="card-right">
            <h3 class="card-right-content">Sales since yesterday</h3>
            <p class="card-right-content">{{ sales_delta }}%</p>
          </div>
        </div>
      </div>
    </div>
    {{#if date_item_counts}}
      <AggChartComponent></AggChartComponent>
    {{/if}}
    <TableComponent></TableComponent>
  </div>
`

let TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate,
  onItemsSelected: function (event, attribute) {
    let totalSelected = this.parent.get('totalSelected');
    if (event.node.checked) {
      this.parent.set('totalSelected', totalSelected + event.context[attribute]);
    }
    else {
      this.parent.set('totalSelected', totalSelected - event.context[attribute]);
    }
  }
});

let AggChartComponent = Ractive.extend({
  template: AggChartTemplate,
  format_columns: function(){
    let date_item_counts = this.parent.get('date_item_counts');
    const allItems = this.parent.get('categories').reduce(function (allItems, category) {
      return allItems.concat(category.items);
    }, []);
    const date_sales = this.parent.get('date_sales');
    let dates = ['x'];
    let item_counts = {}
    let date_sales_column = ['sales']
    for (let item_date in date_item_counts) {
      dates.push(item_date);
      date_sales_column.push(date_sales[item_date]);
      allItems.forEach((item) => {
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
    allItems.forEach((item) =>{
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
});

export const ItemCollectionView = {
  render: function ({ic_id}={}) {
    fetch({
      url: urlFor('view', {resource: 'ic', id: ic_id, root: true})
    }).done(({org_name, org_title, ic_name, ic_title, categories, date_item_counts, date_sales, today_sales, net_sales, sales_delta}) => {
      // Initial render
      let icComponent = new Ractive({
        el: '#main-content-area',
        template: ItemCollectionTemplate,
        data: {
          ic_id: ic_id,
          icTitle: ic_title,
          org_name: org_name,
          ic_name: ic_name,
          categories: categories,
          date_item_counts: _.isEmpty(date_item_counts) ? null : date_item_counts,
          date_sales: date_sales,
          net_sales: net_sales,
          sales_delta: sales_delta,
          today_sales: today_sales,
          totalSelected: 0,
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          }
        },
        components: {TableComponent: TableComponent, AggChartComponent: AggChartComponent}
      });
      SideBarView.render('dashboard', {org_name, org_title, ic_id, ic_title});
      setPageTitle(ic_title);
      NProgress.done();
    });
  }
}
