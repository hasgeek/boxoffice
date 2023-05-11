export const OrdersTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ menuTitle }}</h1>
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
              <td>
                <p class="table-content">
                  <a class="boxoffice-button boxoffice-button-info" href="/admin/o/{{accountName}}/order/{{invoice_no}}" data-navigate>
                    Line Items {{#if loading}}<i class="fa fa-spinner fa-spin"></i>{{/if}}
                  </a>
                </p>
              </td>
              <td>
                <p class="table-content">
                  <a class="boxoffice-button boxoffice-button-info btn-inline" href={{ receipt_url }} target="_blank" >View receipt</a>
                  <a class="boxoffice-button boxoffice-button-primary btn-inline" href={{ assignee_url }} target="_blank" >View assignee details</a>
                  <a class="boxoffice-button boxoffice-button-action btn-inline" href="/admin/menu/{{menuId}}/order/{{id}}/partial_refund" data-navigate>Refund</a>
                </p>
              </td>
            </tr>
            {{#show_order}}
            {{/show_order}}
          {{/orders}}
          </tbody>
        </table>
      </div>
    {{else}}
      <p class="text-center">Currently no orders.</p>
    {{/if}}
  </div>
`;

export { OrdersTemplate as default };
