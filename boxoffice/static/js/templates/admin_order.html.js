
export const OrderTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    {{#order:order}}
      <div class="col-xs-12">
        <table class="table table-hover stats-table table-orders" id='order-table'>
          <thead>   
            <tr>
              <th>#</th>
              <th>Receipt</th>
              <th>Buyer name</th>
              <th data-hide="phone">Buyer email</th>
              <th data-hide="phone, tablet, desktop">Buyer phone</th>
              <th data-hide="phone, tablet, desktop">Amount</th>
              <th data-hide="phone, tablet, desktop">Date</th>
              <th data-hide="phone, tablet, desktop">Order id</th>
              <th data-hide="phone, tablet, desktop">Transaction Status</th>
              <th data-hide="phone, tablet">Details</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td></td>
              <td><p class="table-content">{{#if status === "Purchase Order"}}<span class="text-danger">{{ status }} Order</span> {{else}} {{ invoice_no }} {{/if}}</p></td>
              <td><p class="table-content">{{ buyer_fullname }}</p></td>
              <td><p class="table-content">{{ buyer_email }}</p></td>
              <td><p class="table-content">{{ buyer_phone }}</p></td>
              <td><p class="table-content">{{currency}}{{ amount }}</p></td>
              <td><p class="table-content">{{ order_date }}</p></td>
              <td><p class="table-content">{{ id }}</p></td>
              <td><p class="table-content"><span {{#if status === "Purchase Order"}}class="text-danger"{{/if}}>{{ status }}</span></p></td>
              <td>
                <p class="table-content">
                {{#if status === "Sales Order"}}
                  <a class="boxoffice-button boxoffice-button-small boxoffice-button-info orders-btn" href={{ receipt }} target="_blank" >View Receipt</a>
                  <a class="boxoffice-button boxoffice-button-small boxoffice-button-info right-button orders-btn" href={{ assignee }} target="_blank" >View Assignee details</a>
                {{else}}
                  No details
                {{/if}}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      {{#line_items:line_item}}
        <div class="ticket col-sm-6 col-xs-12" id="item-{{ seq }}">
          <div class="heading">
            <div class="ticket-type">
              <p>{{ title }}</p>
            </div>
          </div>
          <div class="content">
            <div class="content-box">
              <p><span class="italic-title">Ticket id:</span> {{ id }}</p>
              <p><span class="italic-title">Base amount:</span> {{ currency }}{{ base_amount }}</p>
              <p><span class="italic-title">Discounted amount:</span> {{ currency }}{{ discounted_amount }}</p>
              <p><span class="italic-title">Final amount:</span> {{ currency }}{{ final_amount }}</p>
              {{#discount_policy}}<p><span class="italic-title">Discount policy:</span> <span class="line-item-discount">{{ discount_policy }}</span>{{/}}
              {{#discount_coupon}}<p><span class="italic-title">Discount coupon:</span> <span class="line-item-discount">{{ discount_coupon }}</span>{{/}}
              {{#cancelled_at}}<p><b><span class="italic-title cancelled">Cancelled at: {{ formatDate(cancelled_at) }}</span></b></p>{{/}}
              {{#assignee_details}}
                <p><span class="italic-title">Assignee id:</span> {{ id }}</p>
                <p><span class="italic-title">Fullname:</span> {{ fullname }}</p>
                <p><span class="italic-title">Email:</span> {{ email }}</p>
                <p><span class="italic-title">Phone:</span> {{ phone }}</p>
                {{#details:key }}
                  <p><span class="italic-title">{{ key }}:</span> {{ . }}</p>
                {{/}}
              {{else}}
                <p><b>Ticket not assigned</b></p>
              {{/}}
              {{#cancel_ticket_url && !cancelled_at}}
                <p>
                  <button class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="cancelTicket" {{#cancelling}}disabled{{/}}>
                    Cancel Ticket {{#cancelling}}<i class="fa fa-spinner fa-spin"></i>{{/}}
                  </button>
                </p>
                <p class="error-msg">{{cancel_error}}</p>
              {{/}}
            </div>
          </div>
        </div>
      {{/}}
    {{/}}
  </div>
`
