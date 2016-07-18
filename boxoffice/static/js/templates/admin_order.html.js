
export const OrderTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    {{#if orders}}
      <form class="table-title col-sm-6 col-xs-12">
          <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
      </form>
      <div class="table-title form-group text-right col-sm-6 col-xs-12">
        <label for="filter-status" class="status-select-label">Filter:</label>
        <select class="form-control status-select" id="filter-status">
          <option value="">All orders</option>
          <option value="Paid order">Paid orders</option>
          <option value="Free order">Free orders</option>
          <option value="Unpaid order">Unpaid orders</option>
        </select>
      </div>
      <div class="col-xs-12">
        <table class="table table-hover stats-table table-orders footable toggle-circle-filled" id='orders-table' data-filter="#filter">
          <thead>
            <tr>
              <th data-sort-ignore="true">#</th>
              <th data-hide="phone" data-type="numeric" data-sort-initial="true" data-sort-initial="descending">Receipt No.</th>
              <th>Buyer name</th>
              <th data-hide="phone, tablet">Buyer email</th>
              <th data-hide="phone, tablet, desktop">Buyer phone</th>
              <th data-hide="phone, tablet" data-type="numeric">Amount</th>
              <th data-hide="phone, tablet, desktop, largescreen" data-type="numeric">Date</th>
              <th data-hide="phone, tablet, desktop, largescreen">Order id</th>
              <th data-hide="phone, tablet, desktop, largescreen">Transaction status</th>
              <th data-sort-ignore="true">View</th>
              <th data-hide="phone, tablet, desktop, largescreen">Assigment status</th>
              <th data-hide="phone, tablet, desktop, largescreen" data-sort-ignore="true">Details</th>
              <th data-hide="phone, tablet, desktop, largescreen" data-sort-ignore="true">Line items</th>
            </tr>
          </thead>
          <tbody>
          {{#orders:order}}
            <tr id="order-{{ id }}">
              <td></td>
              <td><p class="table-content">{{ invoice_no }}</p></td>
              <td><p class="table-content">{{ buyer_fullname }}</p></td>
              <td><p class="table-content">{{ buyer_email }}</p></td>
              <td><p class="table-content">{{ buyer_phone }}</p></td>
              <td><p class="table-content">{{currency}}{{ amount }}</p></td>
              <td><p class="table-content">{{ order_date }}</p></td>
              <td><p class="table-content">{{ id }}</p></td>
              <td>
                <p class="table-content">
                  {{#if amount === 0}}
                    <span>Free order</span>
                  {{elseif status === "Sales Order"}}
                    <span>Paid order</span>
                  {{elseif status === "Purchase Order"}}
                    <span>Unpaid order</span>
                  {{/if}}
                </p>
              </td>
              <td><p class="table-content"><a class="boxoffice-button boxoffice-button-info orders-sm-btn" href="javascript:void(0)" on-click="showOrder">Line Items</a></p></td>
              <td>
                <p class="table-content">
                  {{#if status === "Sales Order"}}
                    {{#fully_assigned}} Complete {{else}} Pending {{/}}
                  {{/if}}
                  </p>
              </td>
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
              <td>
                <div class="table-content">
                {{#line_items:line_item}}
                  <p>{{@index+1}}. {{ title }}</p>
                {{/}}
                </div>
              </td>
            </tr>
            {{#show_order}}
              <div class="order-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
                <button on-click="hideOrder" class="close-button"><i class="fa fa-close"></i></button>
                <p class="order-title">Order Invoice No: {{invoice_no}}</p>
                <div class="line-items-wrapper">
                  {{#line_items:line_item}}
                    <div class="ticket col-sm-6 col-xs-12" id="item-{{ @index }}">
                      <div class="heading">
                        <div class="ticket-type">
                          <p>{{ title }}</p>
                        </div>
                      </div>
                      <div class="content">
                        <div class="content-box">
                          <p><span class="italic-title">id:</span> {{ id }}</p>
                          <p><span class="italic-title">Base amount:</span> {{ currency }}{{ base_amount }}</p>
                          <p><span class="italic-title">Discounted amount:</span> {{ currency }}{{ discounted_amount }}</p>
                          <p><span class="italic-title">Final amount:</span> {{ currency }}{{ final_amount }}</p>
                          {{#discount_policy}}<p><span class="italic-title">Discount policy:</span> <span class="line-item-discount">{{ discount_policy }}</span>{{/}}
                          {{#discount_coupon}}<p><span class="italic-title">Discount coupon:</span> <span class="line-item-discount">{{ discount_coupon }}</span>{{/}}
                          {{#cancelled_at}}<p><b><span class="italic-title cancelled">Cancelled at: {{ cancelled_at }}</span></b></p>{{/}}
                          {{#assignee_details}}
                            <p><span class="italic-title">Fullname:</span> {{ fullname }}</p>
                            <p><span class="italic-title">Email:</span> {{ email }}</p>
                            <p><span class="italic-title">Phone:</span> {{ phone }}</p>
                            {{#details:key }}
                              <p><span class="italic-title">{{ key }}:</span> {{ . }}</p>
                            {{/}}
                          {{else}}
                            <p><b>Not assigned</b></p>
                          {{/}}
                          {{#cancel_ticket_url && !cancelled_at}}
                            <p>
                              <button class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="cancelTicket" {{#cancelling}}disabled{{/}}>
                                Cancel {{#cancelling}}<i class="fa fa-spinner fa-spin"></i>{{/}}
                              </button>
                            </p>
                            <p class="error-msg">{{cancel_error}}</p>
                          {{/}}
                        </div>
                      </div>
                    </div>
                  {{/}}
                </div>
              </div>
            {{/show_order}}
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
