
export const OrdersTemplate = `
  <div class="ic-main-content">
    <h1 class="header">{{ title }}</h1>
    <div class="col-xs-12">
      <h2>Orders</h2>
      <form class="search-participant clearfix">
          <input autofocus class="form-control search-query" id="search" type="text" name="key" value="" placeholder="Search"/>
      </form>
      {{#if orders}}
        <div class="table-responsive">
          <table class="table table-hover stats-table" id='orders-table'> 
            <thead>   
              <tr>
                <th>#</th>
                <th>Receipt</th>
                <th data-hide="phone, tablet, desktop">Order id</th>
                <th data-hide="phone, tablet, desktop">Transaction Status</th>
                <th>Buyer name</th>
                <th data-hide="phone">Buyer email</th>
                <th data-hide="phone, tablet, desktop">Buyer phone</th>
                <th data-hide="phone, tablet">Amount</th>
                <th data-hide="phone, tablet, desktop">Date</th>
                <th data-hide="phone, tablet">View</th>
              </tr>
            </thead>
            <tbody>
            {{#orders:order}}
              <tr id="order-{{ id }}">
                <td></td>
                <td class="js-searchable">{{ invoice_no }}</td>
                <td class="js-searchable">{{ id }}</td>
                <td class="js-searchable"><span {{#if status === "Incomplete"}}class="text-danger"{{/if}}>{{ status }}</span></td>
                <td class="js-searchable">{{ buyer_fullname }}</td>
                <td class="js-searchable">{{ buyer_email }}</td>
                <td class="js-searchable">{{ buyer_phone }}</td>
                <td class="js-searchable">{{currency}}{{ amount }}</td>
                <td class="js-searchable">{{ order_date }}</td>
                <td><a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="navigate">View Order</a></td>
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
