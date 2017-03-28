
export const OrderTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    {{#if orders}}
      <form class="table-title col-sm-6 col-xs-12" id="search-form">
        <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
      </form>
      <div class="table-title form-group text-right col-sm-6 col-xs-12">
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
              <td><p class="table-content">{{currency}}{{ net_amount }}</p></td>
              <td><p class="table-content">{{ order_date }}</p></td>
              <td><p class="table-content">{{ id }}</p></td>
              <td>
                <p class="table-content">
                  {{#if paid_amount === 0}}
                    <span>Free order</span>
                  {{else}}
                    <span>Paid order</span>
                  {{/if}}
                </p>
              </td>
              <td>
                <p class="table-content"><a class="boxoffice-button boxoffice-button-info" href="javascript:void(0)" on-click="showDetails">Details {{#if loading}}<i class="fa fa-spinner fa-spin"></i>{{/if}}</a>
                </p>
                {{#if net_amount !== 0}}
                  <p class="table-content"><a class="boxoffice-button boxoffice-button-info btn-inline-block" href="javascript:void(0)" on-click="showRefundForm">Refund {{#if showform}}<i class="fa fa-spinner fa-spin"></i>{{/if}}</a>
                  </p>
                {{/if}}
              </td>
              <td>
                <p class="table-content">
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ receipt }} target="_blank" >View Receipt</a>
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ assignee }} target="_blank" >View Assignee details</a>
                </p>
              </td>
            </tr>
            {{#showDetailsSlider}}
              <div class="order-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
                <button on-click="hideDetails" class="close-button"><i class="fa fa-close"></i></button>
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
                            <p class="error-msg left-aligned">{{cancel_error}}</p>
                          {{/}}
                        </div>
                      </div>
                    </div>
                  {{/}}
                </div>
              </div>
            {{/showDetailsSlider}}
            {{#showRefundForm}}
              <div class="order-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
                <button on-click="hideRefundForm" class="close-button"><i class="fa fa-close"></i></button>
                <p class="order-title">Order Invoice No: {{ invoice_no }}</p>
                <div class="line-items-wrapper">
                {{#if refunds}}
                  <div class="ticket col-sm-6 col-xs-12">
                      <div class="heading">
                        <div class="ticket-type">
                          <p>Net total: {{ currency }}{{ net_amount }}</p>
                        </div>
                      </div>
                      <div class="content">
                        <div class="content-box">
                            <p>Refunds:</p>
                            <table class="table stats-table table-hover">
                              <thead>
                                <tr>
                                  <th>Date</th>
                                  <th>Refund reason</th>
                                  <th>Amount</th>
                                </tr>
                              </thead>
                              <tbody>
                              {{#refunds}}
                                <tr>
                                  <td>{{ refunded_at }}</td>
                                  <td>{{ refund_description }}</td>
                                  <td>{{ currency }}{{ refund_amount }}</td>
                                </tr>
                              {{/}}
                              </tbody>
                            </table>
                        </div>
                      </div>
                    </div>
                  {{/if}}
                  <div class="ticket col-sm-6 col-xs-12">
                    <div class="heading">
                      <div class="ticket-type">
                      </div>
                    </div>
                    <div class="content">
                      <div class="content-box">
                        <p class="form-title">Refund form</p>
                        <form role="form" id="refund-form-{{ id }}" name="order-refund-form-{{ id }}">
                          <input type="hidden" name="csrf_token" value="{{ getCsrfToken() }}" />
                          <div class="group">   
                            <input type="number" name="amount" value="{{ .refund.amount }}" min="1" class="group-input {{#if .refund.amount !== undefined &&  .refund.amount !== ""}}filled{{/if}}" />
                            <span class="bar"></span>
                            <label class="group-label">Refund amount</label>
                            {{#.refund.errormsg.amount}}<p class="form-error-msg">{{ refund.errormsg.amount }}</p>{{/}}
                          </div>
                          <div class="group">
                            <input type="text" name="internal_note" value="{{ .refund.internal_note }}" class="group-input {{#.refund.internal_note}}filled{{/if}}" />
                            <span class="bar"></span>
                            <label class="group-label">Internal note about reason for refund</label>
                            {{#.refund.errormsg.internal_note}}<p class="form-error-msg">{{ refund.errormsg.internal_note }}</p>{{/}}
                          </div>
                          <div class="group">
                            <input type="text" name="refund_description" value="{{ .refund.refund_description }}" class="group-input {{#.refund.refund_description}}filled{{/if}}" />
                            <span class="bar"></span>
                            <label class="group-label">Refund description</label>
                            {{#.refund.errormsg.refund_description}}<p class="form-error-msg">{{ .refund.errormsg.refund_description }}</p>{{/}}
                            <p class="form-help-text">This description is mainly used to site reason for refund in the cash receipt.</p>
                          </div>
                          <div class="group">
                            <label class="field-title {{#.refund.note_to_user}}filled{{/if}}">Note to user about reason for refund</label>
                            <textarea class="form-control" name="note_to_user" value="{{ .refund.note_to_user }}"></textarea>
                            {{#.refund.errormsg.note_to_user}}<p class="form-error-msg">{{ .refund.errormsg.note_to_user }}</p>{{/}}
                            <p class="form-help-text">This markdown note is send to user in the refund mail.</p>
                          </div>
                          <p>
                            <button class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="refundOrder" {{#refunding}}disabled{{/}}>
                              Refund {{#refunding}}<i class="fa fa-spinner fa-spin"></i>{{/}}
                            </button>
                          </p>
                          <p>{{ .refund.status }}</p>
                          <p class="error-msg left-aligned">{{ .refund.errormsg.refundError }}</p>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            {{/showRefundForm}}
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
