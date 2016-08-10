
export const DiscountCouponTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    {{#if coupons}}
      <form class="table-title col-sm-4 col-xs-6">
        <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
      </form>
      <div class="col-xs-12">
        <table class="table table-hover stats-table table-orders footable toggle-circle-filled" id="coupons-table" data-filter="#filter">
          <thead>
            <tr>
              <th>Coupon</th>
              <th data-hide="phone, tablet, desktop" data-sort-ignore="true">Usage</th>
              <th data-hide="phone, tablet" data-sort-ignore="true">Available</th>
              <th>Discount policy</th>
              <th data-hide="phone, tablet" data-sort-ignore="true">Discount</th>
              <th data-hide="phone, tablet" data-sort-ignore="true">Buyers</th>
            </tr>
          </thead>
          <tbody>
          {{#coupons:coupon}}
            <tr>
              <td class="code"><p class="table-content">{{ code }}</p></td>
              <td><p class="table-content">{{ usage_limit }}</p></td>
              <td><p class="table-content">{{ available }}</p></td>
              <td class="title"><p class="table-content">{{ discount_policy_title }}</p></td>
              <td>
                {{#is_price_based}}
                  <p class="table-content">{{currency}} {{ discount }}</p>
                {{else}}
                  <p class="table-content">{{ discount }}%</p>
                {{/}}
              </td>
              <td>
                {{#if available < usage_limit}}
                  <p class="table-content">
                    <button class="boxoffice-button boxoffice-button-info orders-sm-btn" href="javascript:void(0)" on-click="showCouponUsage" {{#loading}}disabled{{/}}>
                      View {{#loading}}<i class="fa fa-spinner fa-spin"></i>{{/}}
                    </button>
                  </p>
                {{/if}}
              </td>
            </tr>
            {{#show_coupon_usage}}
              <div class="content-slider" intro-outro='fly:{x:200,y:0,duration:200}'>
                <button on-click="hideCouponUsage" class="close-button"><i class="fa fa-close"></i></button>
                <div class="content-slider-wrapper">
                  <form class="table-title col-sm-6 col-xs-12">
                    <input autofocus class="form-control" id="filter-buyers" type="text" name="key" value="" placeholder="Search"/>
                  </form>
                  <div class="col-xs-12">
                    <table class="table table-hover table-orders stats-table footable toggle-circle-filled" id="{{id}}" data-filter="#filter-buyers">
                      <thead>
                        <tr>
                          <th data-sort-ignore="true">Buyer name</th>
                          <th data-sort-ignore="true">Buyer email</th>
                          <th data-sort-ignore="true">Receipt No:</th>
                          <th data-sort-ignore="true">Items</th>
                        </tr>
                      </thead>
                      <tbody>
                        {{#line_items}}
                          <tr>
                            <td>{{ fullname }}</td>
                            <td>{{ email }}</td>
                            <td>{{ invoice_no }}</td>
                            <td>{{ item_title }}</td>
                          </tr>
                        {{/}}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            {{/show_buyer_details}}
          {{/coupons}}
          </tbody>
        </table>
      </div>
    {{else}}
      <p class="text-center">Currently no coupons.</p>
    {{/if}}
  </div>
`
