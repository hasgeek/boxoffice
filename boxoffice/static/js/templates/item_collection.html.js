export const TableTemplate = `
  <div class="col-xs-12">
    <div class="table-responsive item-stats-table">
      <table class="table table-bordered table-hover stats-table">
        <thead>
          <tr class="info">
            <th>#</th>
            <th>Item</th>
            <th>Available</th>
            <th>Sold</th>
            <th>Free</th>
            <th>Cancelled</th>
            <th>Current Price</th>
            <th>Net Sales</th>
          </tr>
        </thead>
        <tbody>
          {{#items}}
            <tr>
              <td>{{ @index + 1 }}</td>
              <td>{{ title }}</td>
              <td>{{ available }}</td>
              <td>{{ sold }}</td>
              <td>{{ free }}</td>
              <td>{{ cancelled }}</td>
              <td>{{ current_price }}</td>
              <td>{{ net_sales }}</td>
            </tr>
          {{/}}
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
  <h1 class="header">{{ title }}</h1>
  <div class="stats clearfix">
    <div class="col-md-4 col-sm-6 col-xs-12">
      <div class="card clearfix">
        <div class="card-left">
          <p class="card-left-content"><i class="fa fa-plus"></i></p>
        </div>
        <div class="card-right">
          <h3 class="card-right-content">Net sales</h3>
          <p class="card-right-content">{{net_sales}}</p>
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
          <p class="card-right-content">{{today_sales}}</p>
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
          <p class="card-right-content">{{sales_delta}}%</p>
        </div>
      </div>
    </div>
  </div>
  <AggChartComponent></AggChartComponent>
  <TableComponent></TableComponent>
`
