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
                <td>{{ available }}</td>
                <td>{{ sold }} <input type="checkbox" name="sold" on-click="onItemsSelected(event, 'sold')" /></td>
                <td>{{ free }} <input type="checkbox" name="free" on-click="onItemsSelected(event, 'free')" /></td>
                <td>{{ cancelled }}</td>
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
  <div class="content-wrapper">
    <h1 class="header col-xs-12">{{ icTitle }}</h1>
    <div class="title-wrapper col-xs-12">
      <a class="boxoffice-button boxoffice-button-action btn-right" href="/admin/ic/{{ic_id}}/edit" data-navigate>
        Edit item collection
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
    <AggChartComponent></AggChartComponent>
    <TableComponent></TableComponent>
  </div>
`
