
export const OrdersTemplate = `
  <div class="ic-main-content">
    <h1 class="header">{{ title }}</h1>
    <div class="col-xs-12">
      <h2>Orders</h2>
      {{#if orders}}
        <div class="table-responsive">
          <table class="table table-hover stats-table" id='orders-table'> 
            <thead>   
              <tr>
                <th>#</th>
                <th data-hide="phone">Date</th>
                <th>Receipt</th>
                <th data-hide="phone, tablet">Order id</th>
                <th data-hide="phone">Transaction Status</th>
                <th>Buyer name</th>
                <th data-hide="phone, tablet, desktop">Buyer email</th>
                <th data-hide="phone, tablet, desktop">Buyer phone</th>
                <th data-hide="phone, tablet, desktop">Amount</th>
                <th data-hide="phone, tablet">View</th>
              </tr>
            </thead>
            <tbody>
            {{#orders:order}}
              <tr>
                <td>{{ @index + 1 }}</td>
                <td>{{ order_date }}</td>
                <td>{{ invoice_no }}</td>
                <td>{{ id }}</td>
                <td><span {{#if status === "Incomplete"}}class="text-danger"{{/if}}>{{ status }}</span></td>
                <td>{{ buyer_fullname }}</td>
                <td>{{ buyer_email }}</td>
                <td>{{ buyer_phone }}</td>
                <td>{{currency}}{{ amount }}</td>
                <td><a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="{{url}}">View Order</a></td>
              </tr>
            {{/orders}}
            </tbody>
          </table>
        </div>
      {{else}}
        <p class="text-center">Currently no orders.</p>
      {{/if}}
    </div>
  </div>
`
