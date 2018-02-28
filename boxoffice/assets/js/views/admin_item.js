
var Ractive = require('ractive');
var c3 = require("c3");
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, formErrorHandler, getFormParameters, urlFor, setPageTitle, registerSubmitHandler} from '../models/util.js';
import {SideBarView} from './sidebar.js';

const ItemTemplate = `
  <div class="content-wrapper">
    <div class="col-md-10 col-md-offset-1 col-xs-12">
      <div class="has-box">
        <h4>{{ item.title }}</h4>
          <p>{{{ item.description_html }}}</p>
      </div>
    </div>
    <div class="col-md-10 col-md-offset-1 col-xs-12">
      <div class="has-box item-stats">
        <div class="row">
          <div class="col-md-3 col-xs-6">
            <div class="">
              <h4 class="digits">{{ item.sold }}/{{ item.quantity_available }}</h4>
              <p class="text-uppercase callout-text">Tickets sold/available</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if active_price}}
              <h4 class="digits">{{ formatToIndianRupee(item.net_sales) }}</h4>
              {{else}}
              <h4 class="digits">0</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Gross revenue earned</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if active_price}}
              <h4 class="digits">{{ formatToIndianRupee(item.active_price) }}</h4>
              {{else}}
              <h4 class="digits">N/A</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Active Price</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if active_price}}
              <h4 class="digits">{{ item.free }}</h4>
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
    <div class="col-md-5 col-md-offset-1 col-xs-12">
      <h2>Ticket prices</h2>
    </div>
    <div class="col-md-5 col-xs-12">
      <h2 class='dp-header'>Associated discount policies</h2>
    </div>
    <div class="col-md-5 col-md-offset-1 col-xs-12">
      <div class="row">
        <div class="panel panel-default price-panel">
          {{#prices: i}}
            <div class="panel-body bg-light hg-bb">
              {{#if prices[i].showForm}}
                <div intro='fly:{"x":20,"y":"0"}'>
                  <button class="edit-btn pull-right" on-click="hidePriceForm(event, 'edit')"><i class="fa fa-edit"></i></button>
                  <BaseframeForm formTemplate="{{ prices[i].form }}" index="{{ i }}" action="edit" url="{{ postUrl('edit', prices[i].id) }}"></BaseframeForm>
                  <p class="error-msg">{{{ prices[i].errorMsg }}}</p>
                </div>
              {{else}}
                <div class="row">
                  <div class="col-md-4 col-xs-5">
                    <p class="past-price text-uppercase">Past Price</p>
                    <p class="start-time"><strong>Start time</strong> <br>{{ formatDateTime(prices[i].json_start_at) }}</p>
                  </div>
                  <div class="col-md-6 col-xs-5 text-center">
                    <p class="price-digits">{{ formatToIndianRupee(prices[i].amount) }}</p>
                  </div>
                  <div class="col-md-2 col-xs-1 text-right">
                    <!-- TODO: Edit link -->
                  </div>
                </div>
              {{/if}}
            </div>
          {{/prices}}
        </div>
      </div>
    </div>
    <div class="col-md-5 col-xs-12">
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
    </div>
    <div class="col-md-10 col-md-offset-1">
    </div>
    <div class="col-md-10 col-md-offset-1 no-padding">
    </div>
  </div>
`

export const DemandGraphTemplate = `
  <div class="chart-wrapper card">
    <div id="chart" class="sales-chart">
    </div>
  </div>
`

let DemandGraph = Ractive.extend({
  template: DemandGraphTemplate,
  format_columns: function(){
    let price_counts = this.parent.get('demand_curve');
    let xs = Object.keys(price_counts);
    let ys = Object.values(price_counts);
    xs.unshift('x');
    ys.unshift('count');
    return [xs, ys];
  },
  oncomplete: function(){
    console.log(this.format_columns());
    this.chart = c3.generate({
      data: {
        x: 'x',
        columns: this.format_columns(),
        type: 'area',
      },
      axis: {
        x: {
          label: 'Price'
        },
        y: {
          label: 'No. of tickets'
        }
      }
    });
  }
});

export const ItemView = {
  render: function({item_id}={}) {
    fetch({
      url: urlFor('view', {resource: 'item', id: item_id, root: true})
    }).then(function({org_name, demand_curve, org_title, ic_id, ic_title, item, prices, item_form, discount_policies}) {
      let itemComponent = new Ractive({
        el: '#main-content-area',
        template: ItemTemplate,
        components: {DemandGraph: DemandGraph},
        data: {
          item: item,
          prices: prices,
          discount_policies: discount_policies,
          demand_curve: demand_curve,
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          },
          formatDateTime: function (datetime) {
            return Util.formatDateTime(datetime, "dddd, MMMM Do YYYY, h:mmA");
          },
        },
      });

      SideBarView.render('items', {org_name, org_title, ic_id, ic_title});
      setPageTitle("Item", item.title);
      NProgress.done();
    });
  }
}
