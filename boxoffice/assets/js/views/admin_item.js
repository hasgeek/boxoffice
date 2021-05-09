var Ractive = require('ractive');
var c3 = require('c3');
import { eventBus } from './main_admin.js';
var NProgress = require('nprogress');
import { Util, fetch, urlFor, setPageTitle } from '../models/util.js';
import { SideBarView } from './sidebar.js';

const ItemTemplate = `
  <div class="content-wrapper clearfix">
    <div class="col-md-8 col-md-offset-1 col-xs-12">
      <h4>{{ item.title }}</h4>
    </div>
    <div class="col-md-2 col-xs-12">
      <a class="boxoffice-button boxoffice-button-action align-right-btn" href="/admin/item/{{item.id}}/edit" data-navigate>Edit item</a>
    </div>
    <div class="col-md-8 col-md-offset-1 col-xs-12">
      {{#if item.description_html}}
        <!--<div class="has-box">{{{ item.description_html }}}</div>-->
      {{/if}}
    </div>
    <div class="col-md-10 col-md-offset-1 col-xs-12">
      <div class="has-box item-stats">
        <div class="row">
          <div class="col-md-3 col-xs-6">
            <div class="">
              <h4 class="digits">{{ item.sold_count }}/{{ item.quantity_available }}</h4>
              <p class="text-uppercase callout-text">Tickets sold/available</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div>
              {{#if item.net_sales}}
                <h4 class="digits">{{ formatToIndianRupee(item.net_sales) }}</h4>
              {{else}}
                <h4 class="digits">0</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Gross revenue earned</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if item.active_price}}
                <h4 class="digits">{{ formatToIndianRupee(item.active_price) }}</h4>
              {{else}}
                <h4 class="digits">N/A</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Active Price</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if item.free_count}}
                <h4 class="digits">{{ item.free_count }}</h4>
              {{else}}
                <h4 class="digits">0</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Free tickets issued</p>
            </div>
          </div>
          <div class="col-md-12 col-xs-12 graph">
            <DemandGraph></DemandGraph>
          </div>
        </div>
      </div>
    </div>
    <div class="col-md-5 col-md-offset-1">
      <div class="col-md-6 col-xs-12">
        <h2 class='col-header'>Ticket prices</h2>
      </div>
      <div class="col-md-6 col-xs-12">
        <a href="/admin/item/{{item.id}}/price/new" data-navigate class="boxoffice-button boxoffice-button-action align-right-btn">New price</a>
      </div>
      <div class="col-xs-12">
        <div class="row">
          <div class="panel panel-default price-panel">
            {{#prices: i}}
              <div class="panel-body bg-light hg-bb">
                <div class="row">
                  <div class="col-md-4 col-xs-5">
                    {{#if prices[i].tense === 'past'}}
                      <p class="past-price text-uppercase">Past Price</p>
                    {{elseif prices[i].tense == 'upcoming'}}
                      <p class="upcoming-price text-uppercase">Upcoming Price</p>
                    {{else}}
                      <p class="current-price text-uppercase">Current Price</p>
                    {{/if}}
                    <p class="start-time"><strong>Start time</strong> <br>{{ formatDateTime(prices[i].start_at) }}</p>
                  </div>
                  <div class="col-md-6 col-xs-5 text-center">
                    <p class="price-digits">{{ formatToIndianRupee(prices[i].amount) }}</p>
                  </div>
                  <div class="col-md-2 col-xs-1 text-right">
                    <a class="edit-btn" href="/admin/item/{{item.id}}/price/{{prices[i].id}}/edit" data-navigate>Edit</a>
                  </div>
                </div>
              </div>
            {{/prices}}
          </div>
        </div>
      </div>
    </div>
    <div class="col-md-5 col-xs-12">
      <h2 class='col-header'>Associated discount policies</h2>
    </div>
    <div class="col-md-5 col-xs-12">
      {{#if discount_policies}}
        {{#discount_policies: i}}
          <div class="col-xs-12">
            <div class="has-box no-padding">
              <p class="discount-title">{{ discount_policies[i].title }}</p>
              <p class="discount-ticket-amount">Tickets bought: <span class="pull-right">{{discount_policies[i].line_items_count}}</span></p>
              {{#if is_automatic}}
                <p class="discount-type hg-bb">Discount type: <span class="pull-right">Automatic</span></p>
              {{else}}
                <p class="discount-type hg-bb">Discount type: <span class="pull-right">Coupon based</span></p>
              {{/if}}
              <p class="discount-type">Discount rate: <span class="pull-right">{{ discount_policies[i].percentage }}%</span></p>
            </div>
          </div>
        {{/}}
      {{else}}
        <p class='margin-left'>No associated discounts yet. <a href="/admin/o/{{org_name}}/discount_policy" data-navigate>Add</a></p>
      {{/if}}
    </div>
    <div class="col-md-10 col-md-offset-1">
    </div>
    <div class="col-md-10 col-md-offset-1 no-padding">
    </div>
  </div>
`;

export const DemandGraphTemplate = `
  <div class="chart-wrapper card">
    <div id="chart" class="sales-chart">
    </div>
  </div>
`;

let DemandGraph = Ractive.extend({
  template: DemandGraphTemplate,
  format_columns: function () {
    let price_counts = this.parent.get('demand_curve');
    let prices = Object.keys(price_counts);
    let quantity_demanded_counts = ['quantity_demanded'];
    let demand_counts = ['demand'];
    prices.forEach((price) => {
      quantity_demanded_counts.push(price_counts[price]['quantity_demanded']);
      demand_counts.push(price_counts[price]['demand']);
    });
    prices.unshift('x');
    return [prices, quantity_demanded_counts, demand_counts];
  },
  oncomplete: function () {
    this.chart = c3.generate({
      data: {
        x: 'x',
        columns: this.format_columns(),
        types: {
          quantity_demanded: 'area',
          demand: 'spline',
        },
        axes: {
          demand: 'y2',
        },
      },
      axis: {
        x: {
          label: 'Price',
        },
        y: {
          label: 'Quantity demanded',
        },
        y2: {
          show: true,
          label: 'Demand',
        },
      },
    });
  },
});

export const ItemView = {
  render: function ({ item_id } = {}) {
    fetch({
      url: urlFor('view', { resource: 'item', id: item_id, root: true }),
    }).then(function ({
      org_name,
      demand_curve,
      org_title,
      ic_id,
      ic_title,
      item,
      prices,
      discount_policies,
    }) {
      let itemComponent = new Ractive({
        el: '#main-content-area',
        template: ItemTemplate,
        components: { DemandGraph: DemandGraph },
        data: {
          item: item,
          org_name: org_name,
          prices: prices,
          discount_policies: discount_policies,
          demand_curve: demand_curve,
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          },
          formatDateTime: function (datetime) {
            return Util.formatDateTime(datetime, 'dddd, MMMM Do YYYY, h:mmA');
          },
        },
      });

      SideBarView.render('items', { org_name, org_title, ic_id, ic_title });
      setPageTitle('Item', item.title);
      NProgress.done();
    });
  },
};
