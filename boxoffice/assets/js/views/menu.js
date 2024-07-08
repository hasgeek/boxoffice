/* eslint-disable no-unused-vars */
import { Util, fetch, urlFor, setPageTitle } from '../models/util';
import { SideBarView } from './sidebar';

const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');
const NProgress = require('nprogress');
const _ = require('underscore');
const c3 = require('c3');

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
            {{#category.tickets:index}}
              <tr>
                {{#if !index}}
                  <td class="active" rowspan="{{category.tickets.length}}">
                    {{ category.title }}<br />
                    <a href='/admin/menu/{{menuId}}/category/{{category.id}}/edit' data-navigate>Edit</a>
                  </td>
                {{/if}}
                <td>{{ index + 1 }}</td>
                <td><a class="" href="/admin/ticket/{{id}}" data-navigate>{{ title }}</a></td>
                <td>{{ quantity_available }}</td>
                <td>{{ sold_count }} <input type="checkbox" name="sold" on-click="onItemsSelected(event, 'sold_count')" /></td>
                <td>{{ free_count }} <input type="checkbox" name="free" on-click="onItemsSelected(event, 'free_count')" /></td>
                <td>{{ cancelled_count }}</td>
                {{#if active_price}}
                  <td>{{ formatToIndianRupee(active_price) }}</td>
                {{else}}
                  <td>No active price</td>
                {{/if}}
                <td>{{ formatToIndianRupee(netSales) }}</td>
              </tr>
            {{/category.tickets}}
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
`;

export const AggChartTemplate = `
  <div class="chart-wrapper card">
    <div id="chart" class="sales-chart">
    </div>
  </div>
`;

export const MenuTemplate = `
  <div class="content-wrapper clearfix">
    <h1 class="header col-xs-12">{{ menuTitle }}</h1>
    <div class="title-wrapper col-xs-12">
      <a class="boxoffice-button boxoffice-button-info btn-right" href="/{{ accountName }}/{{ menuName }}">
        View listing
      </a>
      <a class="boxoffice-button boxoffice-button-primary btn-right btn-margin-right" href="/admin/menu/{{menuId}}/edit" data-navigate>
        Edit menu
      </a>
      <a class="boxoffice-button boxoffice-button-action btn-right btn-margin-right" href="/admin/menu/{{menuId}}/ticket/new" data-navigate>
        New ticket
      </a>
      <a class="boxoffice-button boxoffice-button-primary btn-right btn-margin-right" href="/admin/menu/{{menuId}}/category/new" data-navigate>
        New category
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
            <p class="card-right-content">{{ formatToIndianRupee(netSales) }}</p>
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
            <p class="card-right-content">{{ formatToIndianRupee(todaySales) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 col-sm-6 col-xs-12">
        <div class="card clearfix">
          <div class="card-left">
            {{#if salesDelta > 0 }}
              <p class="card-left-content"><i class="fa fa-arrow-up"></i></p>
            {{elseif salesDelta < 0 }}
              <p class="card-left-content"><i class="fa fa-arrow-down"></i></p>
            {{else}}
              <p class="card-left-content"><i class="fa fa-minus"></i></p>
            {{/if}}
          </div>
          <div class="card-right">
            <h3 class="card-right-content">Sales since yesterday</h3>
            <p class="card-right-content">{{ salesDelta }}%</p>
          </div>
        </div>
      </div>
    </div>
    {{#if dateItemCounts}}
      <AggChartComponent></AggChartComponent>
    {{/if}}
    <TableComponent></TableComponent>
  </div>
`;

const TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate,
  onItemsSelected(event, attribute) {
    const totalSelected = this.parent.get('totalSelected');
    if (event.node.checked) {
      this.parent.set('totalSelected', totalSelected + event.context[attribute]);
    } else {
      this.parent.set('totalSelected', totalSelected - event.context[attribute]);
    }
  },
});

const AggChartComponent = Ractive.extend({
  template: AggChartTemplate,
  format_columns() {
    const dateItemCounts = this.parent.get('dateItemCounts');
    const allItems = this.parent.get('categories').reduce((givenItems, category) => {
      return givenItems.concat(category.tickets);
    }, []);
    const dateSales = this.parent.get('dateSales');
    const dates = ['x'];
    const itemCounts = {};
    const dateSalesColumn = ['sales'];
    Object.keys(dateItemCounts).forEach((itemDate) => {
      dates.push(itemDate);
      dateSalesColumn.push(dateSales[itemDate]);
      allItems.forEach((ticket) => {
        if (!itemCounts[ticket.id]) {
          itemCounts[ticket.id] = [];
        }
        if (Object.prototype.hasOwnProperty.call(dateItemCounts[itemDate], ticket.id)) {
          // If an item has been bought on this itemDate
          itemCounts[ticket.id].push(dateItemCounts[itemDate][ticket.id]);
        } else {
          // Item not bought on this date
          itemCounts[ticket.id].push(0);
        }
      });
    });

    const columns = [dates];
    allItems.forEach((ticket) => {
      columns.push([ticket.title].concat(itemCounts[ticket.id]));
    });

    // let barGraphHeaders = columns.map((col) => col[0]).filter((header) => header !== 'x');

    columns.push(dateSalesColumn);
    return columns;
  },
  oncomplete() {
    const columns = this.format_columns();
    const barGraphHeaders = _.without(_.map(columns, _.first), 'x', 'sales');

    this.chart = c3.generate({
      data: {
        x: 'x',
        columns: this.format_columns(),
        type: 'bar',
        types: {
          sales: 'line',
        },
        groups: [barGraphHeaders],
        axes: {
          sales: 'y2',
        },
      },
      bar: {
        width: {
          ratio: 0.5, // this makes bar width 50% of length between ticks
        },
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: {
            format: '%d-%m',
          },
          label: 'Date',
        },
        y: {
          label: 'No. of tickets',
        },
        y2: {
          show: true,
          label: 'Sales',
        },
      },
    });

    this.parent.on('data_update', () => {
      this.chart.load({
        columns: this.format_columns(),
      });
    });
  },
});

export const MenuView = {
  render({ menuId } = {}) {
    fetch({
      url: urlFor('view', { resource: 'menu', id: menuId, root: true }),
    }).done(
      ({
        account_name: accountName,
        account_title: accountTitle,
        menu_name: menuName,
        menu_title: menuTitle,
        categories,
        date_item_counts: dateItemCounts,
        date_sales: dateSales,
        today_sales: todaySales,
        net_sales: netSales,
        sales_delta: salesDelta,
      }) => {
        // Initial render
        const icComponent = new Ractive({
          el: '#main-content-area',
          template: MenuTemplate,
          transitions: { fly },
          data: {
            menuId,
            menuTitle,
            accountName,
            menuName,
            categories,
            dateItemCounts: _.isEmpty(dateItemCounts) ? null : dateItemCounts,
            dateSales,
            netSales,
            salesDelta,
            todaySales,
            totalSelected: 0,
            formatToIndianRupee(amount) {
              return Util.formatToIndianRupee(amount);
            },
          },
          components: {
            TableComponent,
            AggChartComponent,
          },
        });
        SideBarView.render('dashboard', {
          accountName,
          accountTitle,
          menuId,
          menuTitle,
        });
        setPageTitle(menuTitle);
        NProgress.done();
      }
    );
  },
};
