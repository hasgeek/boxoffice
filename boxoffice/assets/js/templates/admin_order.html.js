
export const OrderTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ icTitle }}</h1>
    {{#if orders}}
      <form class="title-wrapper col-sm-6 col-xs-12" id="search-form">
        <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
      </form>
      <div class="title-wrapper form-group text-right col-sm-6 col-xs-12">
        <label for="filter-status" class="status-select-label">Filter:</label>
        <select class="form-control status-select" id="filter-status">
          <option value="">All orders</option>
          <option value="Paid order">Paid orders</option>
          <option value="Free order">Free orders</option>
        </select>
      </div>
      <div class="col-xs-12">
        <table class="table table-hover stats-table table-orders footable toggle-circle-filled" id='orders-table' data-filter="#filter" data-page-size="50">
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
              <th data-hide="phone, tablet, desktop, largescreen" data-sort-ignore="true">Details</th>
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
              <td><p class="table-content">{{ formatToIndianRupee(amount) }}</p></td>
              <td><p class="table-content">{{ formatDateTime(order_date) }}</p></td>
              <td><p class="table-content">{{ id }}</p></td>
              <td>
                <p class="table-content">
                  {{#if amount === 0}}
                    <span>Free order</span>
                  {{else}}
                    <span>Paid order</span>
                  {{/if}}
                </p>
              </td>
              <td><p class="table-content"><a class="boxoffice-button boxoffice-button-info" href="javascript:void(0)" on-click="showOrder">Line Items {{#if loading}}<i class="fa fa-spinner fa-spin"></i>{{/if}}</a></p></td>
              <td>
                <p class="table-content">
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ receipt }} target="_blank" >View Receipt</a>
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ assignee }} target="_blank" >View Assignee details</a>
                </p>
              </td>
            </tr>
            {{#show_order}}
              <div class="content-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
                <button on-click="hideOrder" class="close-button"><i class="fa fa-close"></i></button>
                <p class="content-slider-title">Order Invoice No: {{invoice_no}}</p>
                <div class="content-slider-wrapper">
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
                          <p><span class="italic-title">Base amount:</span> {{ formatToIndianRupee(base_amount) }}</p>
                          <p><span class="italic-title">Discounted amount:</span> {{ formatToIndianRupee(discounted_amount) }}</p>
                          <p><span class="italic-title">Final amount:</span> {{ formatToIndianRupee(final_amount) }}</p>
                          {{#discount_policy}}<p><span class="italic-title">Discount policy:</span> <span class="line-item-discount">{{ discount_policy }}</span>{{/}}
                          {{#discount_coupon}}<p><span class="italic-title">Discount coupon:</span> <span class="line-item-discount">{{ discount_coupon }}</span>{{/}}
                          {{#cancelled_at}}<p><b><span class="italic-title cancelled">Cancelled at: {{ formatDateTime(cancelled_at) }}</span></b></p>{{/}}
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
                            <p class="error-msg left-aligned">{{cancel_error}}</p>
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
        </table>
      </div>
    {{else}}
      <p class="text-center">Currently no orders.</p>
    {{/if}}
  </div>
`
