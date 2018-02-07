export const itemTemplate = `
  <div class="content-wrapper">

    <div class="box col-sm-6 col-xs-12">
	    <div class="content">
        <div class="content-box">
          <h4>{{ item.title }}</h4>
          {{{ item.description_html }}}
        </div>
      </div>
    </div>

    <div class="col-xs-12">
      <div class="card clearfix">
        <p class="">
          <b>{{ item.sold }}/{{ item.quantity_available }}</b>
        </p>
        <p class="">
          Sold/Available
        </p>
        <p class="">
          {{#if item.net_sales}}
            <b>{{ formatToIndianRupee(item.net_sales) }}</b>
          {{else}}
            <b>0</b>
          {{/if}}
        </p>
        <p class="">
          Gross revenue earned
        </p>
      </div>
      <div class="card clearfix">
        <p class="">
          {{#if active_price}}
            <b>{{ formatToIndianRupee(item.active_price) }}</b>
          {{else}}
            None
          {{/if}}
        </p>
        <p class="">
          Active price
        </p>
        <p class="">
          <b>{{ item.free }}</b>
        </p>
        <p class="">
          Free
        </p>
      </div>
    </div>

    <div class="col-xs-12">Graph</div>

    <div>
      <h3>Ticket price</h3>
      <div class="box col-xs-6 col-xs-12">
        {{#prices: i}}
          <div class="content">
            {{#if showForm}}
              <div class="heading-edit">
                <button class="edit-btn" on-click="hidePriceForm(event, 'edit')"><i class="fa fa-close"></i></button>
              </div>
              <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                <PriceForm formTemplate="{{ formTemplate }}" price="{{ i }}" priceId="{{ prices[i].id }}" action="edit"></PriceForm>
                <p class="error-msg">{{{ prices[i].errorMsg }}}</p>
              </div>
            {{else}}
              <div class="heading-edit">
                <button class="edit-btn" on-click="showPriceForm(event, 'edit')"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>
              </div>
              <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                <p>start time</p>
                <p>{{ formatDateTime(prices[i].json_start_at) }}</p>
                <p>{{ formatToIndianRupee(prices[i].amount) }}</p>
              </div>
            {{/if}}
          </div>
        {{/prices}}
      </div>
      <div class="box col-xs-6 col-xs-12">
        <div class="content">
          {{#if !priceForm.showForm }}
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <p>Add a new price</p>
              <button class="boxoffice-button boxoffice-button-action btn-right" on-click="showPriceForm(event, 'new')">Create</button>
            </div>
          {{else}}
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <PriceForm formTemplate="{{ priceForm.form }}" action="new"></PriceForm>
              <p class="error-msg">{{{ priceForm.errorMsg }}}</p>
            </div>
          {{/if}}
        </div>
      </div>
    </div>

    <div>
      <h3>Related discount policies</h3>
      {{#discount_policies: i}}
        <div class="box col-sm-4 col-xs-6">
          <p class="title">{{ discount_policies[i].title }}</p>
          <p>Tickets bought with this discount policy</p>
          {{#if discount_policies[i].is_automatic}}
            <p>DISCOUNT TYPE <b>Automatic</b></p>
          {{else}}
              <p>DISCOUNT TYPE <b>Coupon based</b></p>
          {{/if}}
          {{#if discount_policies[i].percentage}}
            <p>DISCOUNT RATE <b>{{ discount_policies[i].percentage }}%</b></p>
          {{elseif discount_policies[i].is_price_based}}
            <p>DISCOUNT RATE <b>{{ formatToIndianRupee(discount_policies[i].price_details.amount) }}</b></p>
          {{/if}}
        </div>
      {{/}}
    </div>

  </div>
`
