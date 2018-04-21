export const OrderTemplate = `
  <div class="content-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
    <a on-click="closeOrder" class="close-button" data-navigate><i class="fa fa-close"></i></a>
    <p class="content-slider-title">Order receipt no: {{order.invoice_no}}</p>
    <br />
    <ul class='content-slider-content'>
      <li>Name: {{order.buyer_fullname}}</li>
      <li>Email: {{order.buyer_email}}</li>
      <li>Phone: {{order.buyer_phone}}</li>
    </ul>
    <p class='content-slider-content'>
      <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ order.receipt_url }} target="_blank" >View receipt</a>
      <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ order.assignee_url }} target="_blank" >View assignee details</a>
      <a class="boxoffice-button boxoffice-button-action btn-inline" href="/admin/ic/{{ic.id}}/order/{{order.id}}/partial_refund" data-navigate>Refund</a>
    </p>
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
                  <button class="boxoffice-button boxoffice-button-small boxoffice-button-action" href="javascript:void(0)" on-click="cancelTicket" {{#cancelling}}disabled{{/}}>
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
`
