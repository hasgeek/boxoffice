
export const OrdersTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <h2 class="col-xs-3">Orders</h2>
    {{#if orders}}
      <form class="search-participant clearfix col-xs-9">
          <input autofocus class="form-control search-query" id="filter" type="text" name="key" value="" placeholder="Search"/>
      </form>
      <div class="table-responsive col-xs-12">
        <table class="table table-hover stats-table table-orders" id='orders-table' data-filter="#filter">
          <thead>   
            <tr>
              <th>#</th>
              <th data-hide="phone">Receipt</th>
              <th>Buyer name</th>
              <th data-hide="phone">Buyer email</th>
              <th data-hide="phone, tablet, desktop">Buyer phone</th>
              <th data-hide="phone, tablet">Amount</th>
              <th data-hide="phone, tablet, desktop">Date</th>
              <th data-hide="phone, tablet, desktop">Order id</th>
              <th data-hide="phone, tablet, desktop">Transaction status</th>
              <th>View</th>
              <th data-hide="phone, tablet, desktop">Ticket Assigment status</th>
              <th data-hide="phone, tablet, desktop">Details</th>
            </tr>
          </thead>
          <tbody>
          {{#orders:order}}
            <tr id="order-{{ id }}">
              <td></td>
              <td><p class="table-content">{{#if status === "Purchase Order"}} <span class="text-danger">{{ status }} Order</span> {{else}} {{ invoice_no }} {{/if}}</p></td>
              <td><p class="table-content">{{ buyer_fullname }}</p></td>
              <td><p class="table-content">{{ buyer_email }}</p></td>
              <td><p class="table-content">{{ buyer_phone }}</p></td>
              <td><p class="table-content">{{currency}}{{ amount }}</p></td>
              <td><p class="table-content">{{ order_date }}</p></td>
              <td><p class="table-content">{{ id }}</p></td>
              <td><p class="table-content"><span {{#if status === "Purchase Order"}} class="text-danger" {{/if}}>{{ status }}</span></p></td>
              <td><p class="table-content"><a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="navigate">Tickets</a></p></td>
              <td><p class="table-content">{{#ticket_assignment}} Complete {{else}} Pending {{/}}</p></td>
              <td>
                <p class="table-content">
                  {{#if status === "Sales Order"}}
                    <a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href={{ receipt }} target="_blank" >View Receipt</a>
                    <a class="boxoffice-button boxoffice-button-small boxoffice-button-info right-button" href={{ assignee }} target="_blank" >View Assignee details</a>
                  {{else}}
                    No details
                  {{/if}}
                </p>
              </td>
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
`
