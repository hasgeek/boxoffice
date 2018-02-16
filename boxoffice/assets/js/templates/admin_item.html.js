export const itemTemplate = `
  <div class="content-wrapper">
    <div class="col-md-8 col-md-offset-1 col-xs-12">
      <a href="" class="edit-page-link"><img src="https://images.hasgeek.com/embed/file/f2fb5593b4024b25968ac10e3cad8fd7" width="14px" alt="" style="margin-top: -4px;"> Edit this page</a>
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
          <div class="panel-body bg-light hg-bb">
            <div class="row ">
              <div class="col-md-4 col-xs-5">
                <p class="past-price text-uppercase">Past Price</p>
                <p class="start-time"><strong>Start time</strong> <br>Wed 7 Feb 2018, 2:00PM</p>
              </div>
              <div class="col-md-6 col-xs-5 text-center">
                <p class="price-digits">₹2000</p>
              </div>
              <div class="col-md-2 col-xs-1 text-right">
                <img class="more-icon" src="https://images.hasgeek.com/embed/file/83ad090da94b44c5890e4936d89451f1" alt="" width="6px">
              </div>
            </div>
          </div>
          <div class="panel-body bg-light hg-bb">
            <div class="row ">
              <div class="col-md-4 col-xs-5">
                <p class="past-price text-uppercase">Past Price</p>
                <p class="start-time"><strong>Start time</strong> <br>Wed 7 Feb 2018, 2:00PM</p>
              </div>
              <div class="col-md-6 col-xs-5 text-center">
                <p class="price-digits">₹2000</p>
              </div>
              <div class="col-md-2 col-xs-1 text-right">
                <img class="more-icon" src="https://images.hasgeek.com/embed/file/83ad090da94b44c5890e4936d89451f1" alt="" width="6px">
              </div>
            </div>
          </div>

          <div class="panel-body bg-highlight hg-bb">
            <div class="row ">
              <div class="col-md-4 col-xs-5">
                <p class="current-price text-uppercase">Current Price</p>
                <p class="start-time"><strong>Start time</strong> <br>Wed 7 Feb 2018, 2:00PM</p>
              </div>
              <div class="col-md-6 col-xs-5 text-center">
                <p class="current-price-digits">₹2000</p>
              </div>
              <div class="col-md-2 col-xs-1 text-right">
                <img class="more-icon" src="https://images.hasgeek.com/embed/file/83ad090da94b44c5890e4936d89451f1" alt="" width="6px">
              </div>
            </div>
          </div>
          <div class="panel-body bg-light hg-bb">
            <div class="row ">
              <div class="col-md-4 col-xs-5">
                <p class="upcoming-price text-uppercase">Upcoming Price</p>
                <p class="start-time"><strong>Start time</strong> <br>Wed 7 Feb 2018, 2:00PM</p>
              </div>
              <div class="col-md-6 col-xs-5 text-center">
                <p class="price-digits">₹2000</p>
              </div>
              <div class="col-md-2 col-xs-1 text-right">
                <img class="more-icon" src="https://images.hasgeek.com/embed/file/83ad090da94b44c5890e4936d89451f1" alt="" width="6px">
              </div>
            </div>
          </div>
          <div class="panel-body bg-light">
            <div class="row ">
              <div class="col-md-4 col-xs-5">
                <p class="upcoming-price text-uppercase">Upcoming Price</p>
                <p class="start-time"><strong>Start time</strong> <br>Wed 7 Feb 2018, 2:00PM</p>
              </div>
              <div class="col-md-6 col-xs-5 text-center">
                <p class="price-digits">₹2000</p>
              </div>
              <div class="col-md-2 col-xs-1 text-right">
                <img class="more-icon" src="https://images.hasgeek.com/embed/file/83ad090da94b44c5890e4936d89451f1" alt="" width="6px">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="col-md-5 col-xs-12">
      <div class="create-new-price text-center">
        <img src="https://images.hasgeek.com/embed/file/5dd8006572a84f7e8c46eeddb76742af" alt="" width="80px">
        <h4 class="color-white">Create new price</h4>
        <button type="button" class="btn btn-hg-primary">Create</button>
      </div>
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
  </div><!-- /.content-wrapper -->


<!-- <div class="content-wrapper">
   <div>
     <h3>Ticket price</h3>
     <div class="box col-xs-6 col-xs-12">
       {{#prices: i}}
         <div class="content">
           <div class="heading-edit">
             <button class="edit-btn" on-click="showPriceForm(event, 'edit')"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>
           </div>
           {{#if showEditForm}}
             <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
               <ICForm formTemplate="{{ formTemplate }}" price="{{ i }}" priceId="{{ prices[i].id }}"></ICForm>
               <p class="error-msg">{{{ prices[i].errorMsg }}}</p>
             </div>
           {{else}}
             <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
               <p>start time</p>
               <p>{{ prices[i].json_start_at }}</p>
               <p>{{ formatToIndianRupee(prices[i].amount) }}</p>
             </div>
           {{/if}}
         </div>
       {{/prices}}
     </div>
      <div class="box col-xs-6 col-xs-12">
        <div class="content">
        {{#if !priceFrom.showAddForm }}
          <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
            <p>Add a new price</p>
             <button class="boxoffice-button boxoffice-button-action btn-right" on-click="showPriceForm(event, 'new')">Create</button>
          </div>
          {{else }}
          <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
            <ICForm formTemplate="{{ priceFrom.form }}"></ICForm>
            <p class="error-msg">{{{ priceForm.errorMsg }}}</p>
          </div>
          {{/if}}
        </div>
      </div>
   </div>
 </div> -->
`
