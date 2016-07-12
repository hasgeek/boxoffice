
export const OrdersTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <div class="col-xs-12">
      <h2>Orders</h2>
      {{#if orders}}
        <form class="search-participant clearfix">
            <input autofocus class="form-control search-query" id="search" type="text" name="key" value="" placeholder="Search"/>
        </form>
        <div class="table-responsive">
          <table class="table table-hover stats-table table-orders" id='orders-table'>
            <thead>   
              <tr>
                <th>#</th>
                <th>Receipt</th>
                <th>Buyer name</th>
                <th data-hide="phone">Buyer email</th>
                <th data-hide="phone, tablet, desktop">Buyer phone</th>
                <th data-hide="phone, tablet">Amount</th>
                <th data-hide="phone, tablet, desktop">Date</th>
                <th data-hide="phone, tablet, desktop">Order id</th>
                <th data-hide="phone, tablet, desktop">Transaction status</th>
                <th data-hide="phone, tablet">View</th>
                <th data-hide="phone, tablet, desktop">Ticket Assigment status</th> 
              </tr>
            </thead>
            <tbody>
            {{#orders:order}}
              <tr id="order-{{ id }}">
                <td></td>
                <td class="js-searchable">{{#if status === "Incomplete"}} <span class="text-danger">{{ status }} Order</span> {{else}} {{ invoice_no }} {{/if}}</td>
                <td class="js-searchable">{{ buyer_fullname }}</td>
                <td class="js-searchable">{{ buyer_email }}</td>
                <td class="js-searchable">{{ buyer_phone }}</td>
                <td class="js-searchable">{{currency}}{{ amount }}</td>
                <td class="js-searchable">{{ formatDate(order_date) }}</td>
                <td class="js-searchable">{{ id }}</td>
                <td class="js-searchable"><span {{#if status === "Incomplete"}} class="text-danger" {{/if}}>{{ status }}</span></td>
                <td><a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="navigate">View Tickets</a></td>
                <td class="js-searchable">{{#ticket_assignment}} Complete {{else}} Pending {{/}}</td>
              </tr>
            {{/orders}}
            </tbody>
            <tfoot>
              <tr>
                <td colspan="10">
                  <div class="pagination pagination-centered"></div>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      {{else}}
        <p class="text-center">Currently no orders.</p>
      {{/if}}
    </div>
  </div>
`
