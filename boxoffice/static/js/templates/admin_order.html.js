
export const OrderTemplate = `
  <div class="ic-main-content">
    <h1 class="header">{{ title }}</h1>
    {{#order:order}}
      <div class="col-xs-12 table-responsive">
        <table class="table table-hover stats-table" id='order-table'> 
          <thead>   
            <tr>
              <th>#</th>
              <th data-hide="phone">Date</th>
              <th>Receipt</th>
              <th data-hide="phone, tablet, desktop">Order id</th>
              <th data-hide="phone">Transaction Status</th>
              <th>Buyer name</th>
              <th data-hide="phone, tablet, desktop">Buyer email</th>
              <th data-hide="phone, tablet, desktop">Buyer phone</th>
              <th data-hide="phone, tablet, desktop">Amount</th>
              <th data-hide="phone, tablet">Details</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td></td>
              <td>{{ order_date }}</td>
              <td>{{ invoice_no }}</td>
              <td>{{ id }}</td>
              <td><span {{#if status === "Incomplete"}}class="text-danger"{{/if}}>{{ status }}</span></td>
              <td>{{ buyer_fullname }}</td>
              <td>{{ buyer_email }}</td>
              <td>{{ buyer_phone }}</td>
              <td>{{currency}}{{ amount }}</td>
              <td>
                {{#if status === "Complete"}}
                  <a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href={{ receipt }} target="_blank" >View Receipt</a>
                  <a class="boxoffice-button boxoffice-button-small boxoffice-button-info right-button" href={{ assignee }} target="_blank" >View Assignee details</a>
                {{/if}}
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
              <p><span class="italic-title">Base amount:</span> {{ currency }}{{ base_amount }}</p>
              <p><span class="italic-title">Discounted amount:</span> {{ currency }}{{ discounted_amount }}</p>
              <p><span class="italic-title">Final amount:</span> {{ currency }}{{ final_amount }}</p>
              {{#discount_policy}}<p><span class="italic-title">Discount policy:</span> <span class="line-item-discount">{{ discount_policy }}</span>{{/}}
              {{#discount_coupon}}<p><span class="italic-title">Discount coupon:</span> <span class="line-item-discount">{{ discount_coupon }}</span>{{/}}
              {{#cancelled_at}}<p><b><span class="italic-title cancelled">Cancelled at: {{ cancelled_at }}</span></b></p>{{/}}
              {{#assignee_details}}
                <p><span class="italic-title">id:</span> {{ id }}</p>
                <p><span class="italic-title">Fullname:</span> {{ fullname }}</p>
                <p><span class="italic-title">Email:</span> {{ email }}</p>
                <p><span class="italic-title">Phone:</span> {{ phone }}</p>
                {{#details:key }}
                  <p><span class="italic-title">{{ key }}:</span> {{ . }}</p>
                {{/}}
              {{else}}
                <p><b>Ticket not assigned</b></p>
              {{/}}
            </div>
          </div>
        </div>
      {{/}}
    {{/}}
  </div>
`
