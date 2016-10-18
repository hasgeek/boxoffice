
export const DiscountPolicyTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <form class="table-title col-sm-4 col-xs-12">
      <input autofocus class="form-control" type="text" on-keyup="searchPolicy" placeholder="Search discount policy"/>
    </form>
    <div class="table-title col-sm-4 col-sm-offset-4 col-xs-12">
      <button class="boxoffice-button boxoffice-button-action btn-right" on-click="openNewPolicyForm">Create discount policy</button>
    </div>
    {{#if show_add_policy_form}}
      <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
        <button on-click="closeNewPolicyForm" class="close-button"><i class="fa fa-close"></i></button>
        <p class="content-slider-title">Add a new discount policy</p>
        <div class="content-slider-wrapper">
          <form role="form" id="new-policy-form" name="adding-new-policy-form"> 
            <div class="group">   
              <input class="group-input {{#new_discount_policy.title}}filled{{/}}" type="text" name="title" value="{{new_discount_policy.title}}">
              <span class="bar"></span>
              <label class="group-label">Title</label>
              {{#new_discount_policy.errormsg.title}}<p class="form-error-msg">{{ new_discount_policy.errormsg.title }}</p>{{/}}
            </div>

            <div class="group">
              <p class="field-title filled">What type of discount?</p>
              <label class="radio-inline">
                <input type="radio" name="is_price_based" value="1" on-click="policyChange" checked>
                Special price
              </label>
              <label class="radio-inline">
                <input type="radio" name="is_price_based" value="0" on-click="policyChange">
                Percentage
              </label>
            </div>

            {{#if new_discount_policy.is_price_based == 0}}
              <div class="group">
                <p class="field-title filled">How is this discount going to be availed?</p>
                <label class="radio-inline">
                  <input type="radio" name="discount_type" value="1" on-click="policyTypeChange" checked>
                  Coupon based
                </label>
                  <label class="radio-inline">
                    <input type="radio" name="discount_type" value="0" on-click="policyTypeChange">
                    Automatic
                  </label>
              </div>
            {{/if}}

            {{#if new_discount_policy.discount_type == 0}}
              <div class="group">   
                <input class="group-input {{#new_discount_policy.item_quantity_min}}filled{{/}}" name="item_quantity_min" value="{{new_discount_policy.item_quantity_min}}">
                <span class="bar"></span>
                <label class="group-label">Minimum number of tickets</label>
                {{#new_discount_policy.errormsg.item_quantity_min}}<p class="form-error-msg">{{ new_discount_policy.errormsg.item_quantity_min }}</p>{{/}}
              </div>
              <p class="form-help-text">For Automatic discounts, minimum number of tickets user needs to buy to avail this discount.<br>Eg:- 5% discount on buying 5 or more tickets.</p>
            {{/if}}

            {{#if new_discount_policy.is_price_based == 1}}
              <p class="field-title filled">What is the discount for?</p>
              <div class="group"> 
                <input id="add-item" name="items" type="hidden">
                {{#new_discount_policy.errormsg.items}}<p class="form-error-msg">{{ new_discount_policy.errormsg.items }}</p>{{/}}
              </div>
              <div class="group">   
                <input class="group-input {{#new_discount_policy.price_title}}filled{{/}}" type="text" name="price_title" value="{{new_discount_policy.price_title}}">
                <span class="bar"></span>
                <label class="group-label">Special price title</label>
                {{#new_discount_policy.errormsg.price_title}}<p class="form-error-msg">{{ new_discount_policy.errormsg.price_title }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#new_discount_policy.amount}}filled{{/}}" name="amount" value="{{new_discount_policy.amount}}">
                <span class="bar"></span>
                <label class="group-label">Special price amount</label>
                {{#new_discount_policy.errormsg.amount}}<p class="form-error-msg">{{ new_discount_policy.errormsg.amount }}</p>{{/}}
              </div>
              <div class="group inline-group clearfix">
                <div class="input-group">
                  <p class="field-title filled">Special price start date</p>
                  <input type="text" class="group-input date" id="start_date" name="start_at" value="{{new_discount_policy.start_at}}" />
                  <i class="fa fa-calendar calendar-icon"></i>
                  {{#new_discount_policy.errormsg.start_at}}<p class="form-error-msg">{{ new_discount_policy.errormsg.start_at }}</p>{{/}}
                </div>
                <div class="input-group">
                  <p class="field-title filled">Special price end date</p>
                  <input type="text" class="group-input date" id="end_date" name="end_at" value="{{new_discount_policy.end_at}}" />
                  <i class="fa fa-calendar calendar-icon"></i>
                  {{#new_discount_policy.errormsg.end_at}}<p class="form-error-msg">{{ new_discount_policy.errormsg.end_at }}</p>{{/}}
                </div>
              </div>
            {{else}}
              <p class="field-title filled">What is the discount for?</p>
              <div class="group">
                <input id="add-items" name="items" type="hidden">
                {{#new_discount_policy.errormsg.items}}<p class="form-error-msg">{{ new_discount_policy.errormsg.items }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#new_discount_policy.percentage}}filled{{/}}" name="percentage" value="{{new_discount_policy.percentage}}">
                <span class="bar"></span>
                <label class="group-label">Discount percentage</label>
                {{#new_discount_policy.errormsg.percentage}}<p class="form-error-msg">{{ new_discount_policy.errormsg.percentage }}</p>{{/}}
              </div>
            {{/if}}

            <input type="hidden" name="organization" required value="{{org}}">
            <div class="btn-wrapper">
              <button type="button" class="boxoffice-button boxoffice-button-info" on-click="closeNewPolicyForm">Back</button>
              <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="addNewPolicy" {{#new_discount_policy.creatingPolicy}}disabled{{/}}>
                Create policy
                {{#new_discount_policy.creatingPolicy}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
              </button>
            </div>
            <p class="error-msg">{{new_discount_policy.generate_policy_error}}</p>
          </form>
        </div>
      </div>
    {{/if}}

    {{#if discount_policies}}
      <div class="policies-wrapper">
        {{#discount_policies}}
          <div class="box col-sm-6 col-xs-12">
            <div class="heading">
              <p class="heading-title">{{ title }}</p>
              <div class="heading-edit">
                {{#if !hide_edit_btn}}<button class="edit-btn" on-click="editPolicyForm"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>{{/if}}
              </div>
            </div>
            <div class="content">
              {{#if !show_policy_form && !show_add_coupon_form}}
                <div class="content-box">
                  <p class="content-details"><b>Discount type:</b></p>
                  <p class="content-details-text">{{discount_type}}</p>

                  {{#if discount_type == "Automatic"}}
                    <p class="content-details"><b>Minimum item quanity:</b></p>
                    <p class="content-details-text">{{item_quantity_min}}</p>
                  {{/if}}

                  {{#if is_price_based}}
                    <p class="content-details"><b>Discount:</b></p>
                    <p class="content-details-text">{{currency}}{{price_details.amount}}</p>
                  {{else}}
                    <p class="content-details"><b>Discount:</b></p>
                    <p class="content-details-text">{{discount}}%</p>
                  {{/if}}

                  {{#if dp_items}}
                    <p class="content-details"><b>Items:</b></p>                   
                    <ol class="content-list">
                      {{#dp_items:item}}
                        <li class="content-details">{{dp_items[item].title}}</li>
                      {{/}}
                    </ol>
                  {{/if}}
                  {{#if discount_type == "Coupon based"}}
                    <button class="boxoffice-button boxoffice-button-action btn-right" on-click="listCoupons">
                      List coupons{{#loadingCoupons}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                    </button>
                    <button class="boxoffice-button boxoffice-button-action btn-right btn-inline" on-click="generateCouponForm">Generate coupon</button>
                    <p class="error-msg">{{loading_coupon_error}}</p>
                  {{/if}}
                </div>
              {{elseif show_policy_form}}
                <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                  <h4 class="text-center form-title">Edit</h4>   
                  <form role="form" id="policy-form-{{id}}" name="edit-policy-form-{{id}}"> 
                    <div class="group">   
                      <input class="group-input {{#title}}filled{{/}}" type="text" name="title" value="{{title}}" twoway="false">
                      <span class="bar"></span>
                      <label class="group-label">Title</label>
                      {{#errormsg.title}}<p class="form-error-msg">{{ errormsg.title }}</p>{{/}}
                    </div>
                    {{#if discount_type == "Automatic"}}
                      <div class="group">   
                        <input class="group-input {{#item_quantity_min}}filled{{/}}" name="item_quantity_min" value="{{item_quantity_min}}" twoway="false">
                        <span class="bar"></span>
                        <label class="group-label">Minimum item quanity</label>
                        {{#errormsg.item_quantity_min}}<p class="form-error-msg">{{ errormsg.item_quantity_min }}</p>{{/}}
                      </div>
                    {{/if}}
                    {{#if is_price_based}}
                      {{#price_details}}
                        <div class="group">   
                          <input class="group-input {{#price_title}}filled{{/}}" type="text" name="price_title" value="{{price_title}}" twoway="false">
                          <span class="bar"></span>
                          <label class="group-label">Price title</label>
                          {{#errormsg.price_title}}<p class="form-error-msg">{{ errormsg.price_title }}</p>{{/}}
                        </div>
                        <div class="group">   
                          <input class="group-input {{#amount}}filled{{/}}" name="amount" value="{{amount}}" twoway="false">
                          <span class="bar"></span>
                          <label class="group-label">Amount</label>
                          {{#errormsg.amount}}<p class="form-error-msg">{{ errormsg.amount }}</p>{{/}}
                        </div>
                        <div class="group">   
                          <p class="field-title filled">Price start date</p>
                          <input type="text" class="group-input date" id="start_date_{{id}}" name="start_at" value="{{start_at}}" twoway="false"/>
                          <i class="fa fa-calendar calendar-icon"></i>
                          {{#errormsg.start_at}}<p class="form-error-msg">{{ errormsg.start_at }}</p>{{/}}
                        </div>
                        <div class="group">   
                          <p class="field-title filled">Price end date</p>
                          <input type="text" class="group-input date" id="end_date_{{id}}" name="end_at" value="{{end_at}}" twoway="false"/>
                          <i class="fa fa-calendar calendar-icon"></i>
                          {{#errormsg.end_at}}<p class="form-error-msg">{{ errormsg.end_at }}</p>{{/}}
                        </div>
                        <div class="group"> 
                          <input id="add-item-{{id}}" name="item" type="hidden" value="{{get_discounted_items(dp_items)}}">
                          {{#errormsg.item}}<p class="form-error-msg">{{ errormsg.item }}</p>{{/}}
                        </div>
                      {{/}}
                    {{else}}
                      <div class="group">   
                        <input class="group-input {{#percentage}}filled{{/}}" name="percentage" value="{{percentage}}" twoway="false">
                        <span class="bar"></span>
                        <label class="group-label">Percentage</label>
                        {{#errormsg.percentage}}<p class="form-error-msg">{{ errormsg.percentage }}</p>{{/}}
                      </div>
                      <div class="group"> 
                        <input id="add-items-{{id}}" name="items" type="hidden" value="{{get_discounted_items(dp_items)}}">
                        {{#errormsg.items}}<p class="form-error-msg">{{ errormsg.items }}</p>{{/}}
                      </div>
                    {{/if}}
                    <div class="btn-wrapper">
                      <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hideEditPolicy">Back</button>                    
                      <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="editPolicy" {{#editingPolicy}}disabled{{/}}>
                          Update policy
                          {{#editingPolicy}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                      </button>
                    </div>
                    <p class="error-msg">{{edit_policy_error}}</p>
                  </form>
                </div>
              {{elseif show_add_coupon_form}}
                <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                  <h4 class="text-center form-title">Generate coupon</h4>
                  <form role="form" id="new-coupon-{{id}}" name="generate-coupon-form-{{id}}">
                    <div class="group">   
                      <input class="group-input {{#count}}filled{{/}}" name="count" value="{{.count}}">
                      <span class="bar"></span>
                      <label class="group-label">How many coupons?</label>
                      {{#errormsg.count}}<p class="form-error-msg">{{ errormsg.count }}</p>{{/}}
                    </div>
                    {{#if count == 1}}
                      <div class="group">   
                        <input class="group-input {{#coupon_code}}filled{{/}}" type="text" name="coupon_code" value="{{.coupon_code}}">
                        <span class="bar"></span>
                        <label class="group-label">What coupon code?</label>
                      </div>
                      <p class="form-help-text">Eg: Hasjob</p>
                    {{/if}}
                      <div class="group">   
                        <input class="group-input filled {{#if count > 1}}disabled{{/if}}" name="usage_limit" value="{{#if count >1 }} 1 {{else}} 1 {{/if}}" {{#if count > 1}}readonly{{/if}}>
                        <span class="bar"></span>
                        <label class="group-label">How many times can this coupon be used?</label>
                        {{#errormsg.usage_limit}}<p class="form-error-msg">{{ errormsg.usage_limit }}</p>{{/}}
                      </div>
                    <div class="btn-wrapper">
                      <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hidegenerateCouponForm">Back</button>
                      <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="generateCoupon" {{#generatingCoupon}}disabled{{/}}>
                          Generate
                          {{#generatingCoupon}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                      </button>
                    </div>
                    <p class="error-msg">{{generate_coupon_error}}</p>
                  </form>
                </div>
              {{/if}}
            </div>

            <div class="modal" id="list-coupons-{{id}}" tabindex="-1" role="dialog">
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title">Discount Coupons</h4>
                  </div>
                  <div class="modal-body clearfix">
                   {{#if coupons}}
                      <form class="table-title col-sm-4 col-xs-6">
                        <input autofocus class="form-control" id="filter-{{id}}" type="text" name="key" value="" placeholder="Search coupon"/>
                      </form>
                      <div class="col-xs-12">
                        <table class="table table-hover stats-table table-orders footable toggle-circle-filled" id="coupons-list-{{id}}" data-filter="#filter-{{id}}">
                          <thead>
                            <tr>
                              <th data-sort-ignore="true">Coupon</th>
                              <th data-sort-ignore="true">Usage</th>
                              <th data-sort-ignore="true">Available</th>
                            </tr>
                          </thead>
                          <tbody>
                          {{#coupons:coupon}}
                            <tr>
                              <td class="code"><p class="table-content">{{ code }}</p></td>
                              <td><p class="table-content">{{ usage_limit }}</p></td>
                              <td><p class="table-content">{{ available }}</p></td>
                            </tr>
                          {{/coupons}}
                          </tbody>
                        </table>
                      </div>
                    {{else}}
                      <p class="text-center">Currently no coupons.</p>
                    {{/if}}
                  </div>
                  <div class="modal-footer">
                    <button class="boxoffice-button boxoffice-button-action btn-right copy-coupons-list" data-clipboard-target="#coupons-list-{{id}}">Copy to clipboard</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="modal" id="generated-coupons-{{id}}" tabindex="-1" role="dialog">
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title">{{ title }}</h4>
                  </div>
                  <div class="modal-body">
                    <p>Discount coupons:</p>
                    <p>The discount will be auto applied on adding the coupon to the event website url. <br>Eg: "https://jsfoo.in/2016<b>?code=xyz123</b>"</p>
                    <div id="new-coupons-{{id}}">
                      {{#coupons:coupon}}
                        <p class="content-details">{{coupons[coupon].code}}</p>
                      {{/}}
                    </div>
                  </div>
                  <div class="modal-footer">
                    <button class="boxoffice-button boxoffice-button-action btn-right copy-coupons" data-clipboard-target="#new-coupons-{{id}}">Copy to clipboard</button>
                  </div>
                </div>
              </div>
            </div>

          </div>
        {{/}}
      </div>
    {{else}}
      <p class="text-center">Currently no discount policies.</p>
    {{/if}}
  </div>
`
