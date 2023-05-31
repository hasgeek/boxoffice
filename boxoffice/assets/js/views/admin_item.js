/* eslint-disable no-unused-vars */
import { Util, fetch, urlFor, setPageTitle } from '../models/util';
import { SideBarView } from './sidebar';

const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');
const c3 = require('c3');

const NProgress = require('nprogress');

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
      {{#if discountPolicies}}
        {{#discountPolicies: i}}
          <div class="col-xs-12">
            <div class="has-box no-padding">
              <p class="discount-title">{{ discountPolicies[i].title }}</p>
              <p class="discount-ticket-amount">Tickets bought: <span class="pull-right">{{discountPolicies[i].line_items_count}}</span></p>
              {{#if is_automatic}}
                <p class="discount-type hg-bb">Discount type: <span class="pull-right">Automatic</span></p>
              {{else}}
                <p class="discount-type hg-bb">Discount type: <span class="pull-right">Coupon based</span></p>
              {{/if}}
              <p class="discount-type">Discount rate: <span class="pull-right">{{ discountPolicies[i].percentage }}%</span></p>
            </div>
          </div>
        {{/}}
      {{else}}
        <p class='margin-left'>No associated discounts yet. <a href="/admin/o/{{accountName}}/discount_policy" data-navigate>Add</a></p>
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

const DemandGraph = Ractive.extend({
  template: DemandGraphTemplate,
  format_columns() {
    const priceCounts = this.parent.get('demandCurve');
    const prices = Object.keys(priceCounts);
    const quantityDemandedCounts = ['quantity_demanded'];
    const demandCounts = ['demand'];
    prices.forEach((price) => {
      quantityDemandedCounts.push(priceCounts[price].quantity_demanded);
      demandCounts.push(priceCounts[price].demand);
    });
    prices.unshift('x');
    return [prices, quantityDemandedCounts, demandCounts];
  },
  oncomplete() {
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
  render({ ticketId } = {}) {
    fetch({
      url: urlFor('view', { resource: 'item', id: ticketId, root: true }),
    }).then(
      ({
        account_name: accountName,
        demand_curve: demandCurve,
        account_title: accountTitle,
        menu_id: menuId,
        menu_title: menuTitle,
        ticket: item,
        prices,
        discount_policies: discountPolicies,
      }) => {
        const itemComponent = new Ractive({
          el: '#main-content-area',
          template: ItemTemplate,
          components: { DemandGraph },
          transitions: { fly },
          data: {
            item,
            accountName,
            prices,
            discountPolicies,
            demandCurve,
            formatToIndianRupee(amount) {
              return Util.formatToIndianRupee(amount);
            },
            formatDateTime(datetime) {
              return Util.formatDateTime(datetime, 'dddd, MMMM Do YYYY, h:mmA');
            },
          },
        });

        SideBarView.render('items', {
          accountName,
          accountTitle,
          menuId,
          menuTitle,
        });
        setPageTitle('Item', item.title);
        NProgress.done();
      }
    );
  },
};
