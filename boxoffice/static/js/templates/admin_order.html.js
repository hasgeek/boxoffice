
export const OrderTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ icTitle }}</h1>
    {{#if orders}}
      <div class="title-wrapper col-sm-4 col-xs-12">
        <input type="text" autofocus class="form-control" placeholder="Search orders" value="{{searchText}}" />
        {{#searchText}}<a on-click="clearSearchField()" class="clear-field"><i class="fa fa-close"></i></a>{{/}}
      </div>
      <div class="col-xs-12">
        <table class="table table-hover stats-table table-orders footable toggle-circle-filled" id='orders-table'>
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
              <th data-hide="phone, tablet, desktop, largescreen">Attendee details</th>
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
              <td><p class="table-content">{{ is_fully_assigned }}</p></td>
              <td><p class="table-content"><a class="boxoffice-button boxoffice-button-info" href="javascript:void(0)" on-click="showOrder(event)">Line Items {{#if loading}}<i class="fa fa-spinner fa-spin"></i>{{/if}}</a></p></td>
              <td>
                <p class="table-content">
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ receipt }} target="_blank" >View Receipt</a>
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ assignee }} target="_blank" >View Assignee details</a>
                </p>
              </td>
            </tr>
            {{#show_order}}
              <div class="content-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
                <button on-click="hideOrder(event)" class="close-button"><i class="fa fa-close"></i></button>
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
                              <button class="boxoffice-button boxoffice-button-small boxoffice-button-info" href="javascript:void(0)" on-click="cancelTicket(event)" {{#cancelling}}disabled{{/}}>
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
        {{#if paginated}}
        <div class="text-center">
          <nav aria-label="Page navigation">
            <ul class="pagination">
              <li>
                {{#if currentPage == 1}}
                  <a href="#" on-click="paginate(event, 1)" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                {{else}}
                  <a href="#" on-click="paginate(event, currentPage - 1)" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                {{/if}}
              </li>
              {{#pages:index}}
              <li {{#if currentPage == pages[index]}}class="active"{{/if}} ><a href="#" on-click="paginate(event, pages[index])">{{pages[index]}}</a></li>
              {{/}}
              <li>
                {{#if currentPage == totalPages}}
                  <a href="#" on-click="paginate(event, totalPages)" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                {{else}}
                  <a href="#" on-click="paginate(event, currentPage + 1)" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                {{/if}}
              </li>
            </ul>
          </nav>
        </div>
        {{/if}}
      </div>
    {{else}}
      <p class="text-center">Currently no orders.</p>
    {{/if}}
  </div>
`
