
export const OrdersTemplate = `
  <div class="ic-main-content">
    <h1 class="header">{{ title }}</h1>
    <div class="col-xs-12">
      <h2>Orders</h2>
      {{#if orders}}
        <div class="table-responsive item-stats-table">
          <table class="table table-bordered table-hover stats-table" id='orders-table'> 
            <thead>   
              <tr>
                <th>#</th>
                <th>Date</th>
                <th>Order No:</th>
                <th>Transaction Status</th>
                <th>Buyer name</th>
                <th>Buyer email</th>
                <th>Buyer phone</th>
                <th>Attendee list</th>
              </tr>
            </thead>
            <tbody>
            {{#orders:order}}
              <tr>
                <td>{{ @index + 1 }}</td>
                <td>{{ order_date }}</td>
                <td>{{ invoice_no }}</td>
                <td><span {{#if status === "Incomplete"}}class="text-danger"{{/if}}>{{ status }}</span></td>
                <td>{{ buyer_fullname }}</td>
                <td>{{ buyer_email }}</td>
                <td>{{ buyer_phone }}</td>
                <td>
                  <ol class="line-item-details">
                    {{#line_items:line_item}}
                      <li>
                        <span>{{ title }}</span>
                        {{#if discount_policy}}
                          <p class="line-item-discount">Discount: {{ discount_policy }} - {{ discount_coupon }}</p>
                        {{/if}}
                      </li>
                    {{/line_items}}
                  </ol>
                  {{#if status === "Complete"}}
                    <p><a class="boxoffice-button boxoffice-button-small boxoffice-button-info" href={{ assignee_details }} target="_blank" >Assignee details</a></p>
                  {{/if}}
                </td>
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