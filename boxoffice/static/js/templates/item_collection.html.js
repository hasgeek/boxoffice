export const TableTemplate = `
  <div class="table-responsive stats">
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
`

export const AggChartTemplate = `
  <div id="chart" class="c3" style="max-height: 280px; position: relative;">
  </div>
`

export const ItemCollectionTemplate = `
  <br>
  <div class="row">
    <div class="col-md-4">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Net Sales</h3>
        </div>
        <div class="panel-body">
          {{net_sales}}
        </div>
      </div>
    </div>
  </div>
  <hr>
  <AggChartComponent></AggChartComponent>
  <hr>
  <TableComponent></TableComponent>
`
