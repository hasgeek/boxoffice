export const itemTemplate = `
  <div class="content-wrapper">
    <div class="col-md-8 col-md-offset-1 col-xs-12">
      <div class="has-box">
        <h4>{{ item.title }}</h4>
          <p>{{{ item.description_html }}}</p>
      </div>
    </div>
    <div class="col-md-10 col-md-offset-1 col-xs-12">
      <div class="has-box item-stats">
        <div class="row">
          <div class="col-md-3 col-xs-6">
            <div class="">
              <h4 class="digits">{{ item.sold }}/{{ item.quantity_available }}</h4>
              <p class="text-uppercase callout-text">Tickets sold/available</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if active_price}}
              <h4 class="digits">{{ formatToIndianRupee(item.net_sales) }}</h4>
              {{else}}
              <h4 class="digits">0</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Gross revenue earned</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if active_price}}
              <h4 class="digits">{{ formatToIndianRupee(item.active_price) }}</h4>
              {{else}}
              <h4 class="digits">N/A</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Active Price</p>
            </div>
          </div>
          <div class="col-md-3 col-xs-6">
            <div class="">
              {{#if active_price}}
              <h4 class="digits">{{ item.free }}</h4>
              {{else}}
              <h4 class="digits">0</h4>
              {{/if}}
              <p class="text-uppercase callout-text">Free tickets issued</p>
            </div>
          </div>
          <div class="col-md-12 col-xs-12 graph">
            <img src="https://dummyimage.com/1000x300/ffffff/000000&text=..." alt="" class="img-responsive hg-bt">
          </div>
        </div>
      </div>
    </div>
    <div class="col-md-10 col-md-offset-1 col-xs-12">
      <h2>Ticket Price</h2>
    </div>
    <div class="col-md-5 col-md-offset-1 col-xs-12">
      <div class="row">
        <div class="panel panel-default price-panel">
          {{#prices: i}}
            <div class="panel-body bg-light hg-bb">
              {{#if prices[i].showForm}}
                <div intro='fly:{"x":20,"y":"0"}'>
                  <button class="edit-btn pull-right" on-click="hidePriceForm(event, 'edit')"><i class="fa fa-edit"></i></button>
                  <BaseframeForm formTemplate="{{ prices[i].form }}" index="{{ i }}" action="edit" url="{{ postUrl('edit', prices[i].id) }}"></BaseframeForm>
                  <p class="error-msg">{{{ prices[i].errorMsg }}}</p>
                </div>
              {{else}}
                <div class="row">
                  <div class="col-md-4 col-xs-5">
                    <p class="past-price text-uppercase">Past Price</p>
                    <p class="start-time"><strong>Start time</strong> <br>{{ formatDateTime(prices[i].json_start_at) }}</p>
                  </div>
                  <div class="col-md-6 col-xs-5 text-center">
                    <p class="price-digits">{{ formatToIndianRupee(prices[i].amount) }}</p>
                  </div>
                  <div class="col-md-2 col-xs-1 text-right">
                    <button class="edit-btn" on-click="showPriceForm(event, 'edit')"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>
                  </div>
                </div>
              {{/if}}
            </div>
          {{/prices}}
        </div>
      </div>
    </div>
    <div class="col-md-5 col-xs-12">
      {{#if priceForm.showForm }}
        <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
          <button on-click="hidePriceForm(event, 'new')" class="edit-btn pull-right"><i class="fa fa-close"></i></button>
          <BaseframeForm formTemplate="{{ priceForm.form }}" index="" action="new" url="{{ postUrl('new') }}"></BaseframeForm>
          <p class="error-msg">{{{ priceForm.errorMsg }}}</p>
        </div>
      {{else}}
        <div class="create-new-price text-center">
          <img src="https://images.hasgeek.com/embed/file/5dd8006572a84f7e8c46eeddb76742af" alt="" width="80px">
          <h4 class="color-white">Create new price</h4>
          <button class="btn btn-hg-primary" on-click="showPriceForm(event, 'new')">Create</button>
        </div>
      {{/if}}
    </div>
    <div class="col-md-10 col-md-offset-1">
      <h2>Related discount policies</h2>
    </div>
    <div class="col-md-10 col-md-offset-1 no-padding">
      {{#discount_policies: i}}
      <div class="col-md-4">
        <div class="has-box no-padding">
          <p class="discount-title">{{ discount_policies[i].title }}</p>
          <p class="discount-ticket-amount">Tickets bought with this discount policy</p>
          {{#if is_automatic}}
          <p class="discount-type hg-bb">Discount type: <span class="pull-right">Automatic</span></p>
          {{else}}
          <p class="discount-type hg-bb">Discount type: <span class="pull-right">Coupon based</span></p>
          {{/if}}
          <p class="discount-type">Discount rate: <span class="pull-right">{{ discount_policies[i].percentage }}%</span></p>
        </div>
      </div>
      {{/}}
    </div>
  </div>
`
