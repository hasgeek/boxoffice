
export const DiscountPolicyTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <form class="table-title col-sm-4 col-xs-12">
      <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
    </form>
    <div class="table-title col-sm-4 col-sm-offset-4 col-xs-12">
      <button class="boxoffice-button boxoffice-button-action btn-right" on-click="addNewPolicyForm">Create discount policy</button>
    </div>
    {{#if show_add_policy_form}}
      <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
        <button on-click="hideNewPolicyForm" class="close-button"><i class="fa fa-close"></i></button>
        <p class="content-slider-title">Add discount policy form</p>
        <div class="content-slider-wrapper">
          <form role="form" id="new-policy-form"> 
            <div class="group">   
              <input class="group-input {{#new_discount_policy.title}}filled{{/}}" type="text" name="title" required value="{{new_discount_policy.title}}">
              <span class="bar"></span>
              <label class="group-label">Title</label>
            </div>
            <div class="group">
              <label class="checkbox-inline">
                <input type="checkbox" name="is_price_based" value=1 checked="{{new_discount_policy.is_price_based}}">
                Price based discount policy
              </label>
            </div>
            <div class="group">
              <p class="field-title filled">Discount type</p>
              <label class="radio-inline">
                <input type="radio" name="discount_type" value=1 on-click="policyChange(event)" checked>
                Coupon based
              </label>
              {{^new_discount_policy.is_price_based}}
                <label class="radio-inline">
                  <input type="radio" name="discount_type" value=0 on-click="policyChange(event)">
                  Automatic
                </label>
              {{/}}
            </div>

            {{#if new_discount_policy.discount_type == 1}}
              <div class="group">   
                <input class="group-input {{#new_discount_policy.item_quantity_min}}filled{{/}}" type="number" name="item_quantity_min" required min="1" value="{{new_discount_policy.item_quantity_min}}">
                <span class="bar"></span>
                <label class="group-label">Minimum item quanity</label>
              </div>
            {{/if}}

            {{#if new_discount_policy.is_price_based}}
              <div class="group"> 
                <input id="add-item" name="items" type="hidden" required>
              </div>
              <div class="group">   
                <input class="group-input {{#new_discount_policy.price_title}}filled{{/}}" type="text" name="price_title" required value="{{new_discount_policy.price_title}}">
                <span class="bar"></span>
                <label class="group-label">Price title</label>
              </div>
              <div class="group">
                <input class="group-input {{#new_discount_policy.amount}}filled{{/}}" type="number" name="amount" required min="0" value="{{new_discount_policy.amount}}">
                <span class="bar"></span>
                <label class="group-label">Amount</label>
              </div>
              <div class="group inline-group"> 
                <div class="input-group">
                  <p class="field-title filled">Price start date</p>
                  <input type="text" class="group-input date" id="start_date" data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker" name="start_at" value={{new_discount_policy.start_at}} />
                  <i class="fa fa-calendar calendar-icon"></i>
                </div>
                <div class="input-group">
                  <p class="field-title filled">Price end date</p>
                  <input type="text" class="group-input date" id="end_date" data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker" name="end_at" value={{new_discount_policy.end_at}} />
                  <i class="fa fa-calendar calendar-icon"></i>
                </div>
              </div>
            {{else}}
              <div class="group"> 
                <input id="add-items" name="items" type="hidden" required>
              </div>
              <div class="group">   
                <input class="group-input {{#new_discount_policy.percentage}}filled{{/}}" type="number" name="percentage" required min="1" value="{{new_discount_policy.percentage}}">
                <span class="bar"></span>
                <label class="group-label">Percentage</label>
              </div>
            {{/if}}

            <input type="hidden" name="organization" required value="{{org}}">
            <div class="btn-wrapper">
              <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hideNewPolicyForm">Back</button>
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
                  {{#if coupons}}
                    <p class="content-details"><b>Recently generated coupons:</b></p>
                    <ul class="content-list">
                    {{#coupons:coupon}}
                       <li class="content-details"><b>{{coupons[coupon].code}}</b>, usage limit: {{coupons[coupon].usage_limit}}</li>
                    {{/}}
                    </ul>
                  {{/if}}
                  <div class="modal" id="coupons-{{id}}" tabindex="-1" role="dialog">
                    <div class="modal-dialog" role="document">
                      <div class="modal-content">
                        <div class="modal-header">
                          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                          <h4 class="modal-title">{{ title }}</h4>
                        </div>
                        <div class="modal-body">
                          <p>Discount coupons:</p>
                          {{#coupons:coupon}}
                            <p class="content-details">{{coupons[coupon].code}}</p>
                          {{/}}
                        </div>
                      </div>
                    </div>
                  </div>
                  {{#if discount_type == "Coupon based"}}
                    <button class="boxoffice-button boxoffice-button-action btn-right" on-click="generateCouponForm">Generate coupon</button>
                  {{/if}}
                </div>
              {{elseif show_policy_form}}
                <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                  <h4 class="text-center form-title">Please fill the attendee details</h4>   
                  <form role="form" id="policy-form-{{id}}"> 
                    <div class="group">   
                      <input class="group-input {{#title}}filled{{/}}" type="text" name="title" required value="{{title}}" twoway="false">
                      <span class="bar"></span>
                      <label class="group-label">Title</label>
                    </div>
                    {{#if discount_type == "Automatic"}}
                      <div class="group">   
                        <input class="group-input {{#item_quantity_min}}filled{{/}}" type="number" name="item_quantity_min" required min="1" value="{{item_quantity_min}}" twoway="false">
                        <span class="bar"></span>
                        <label class="group-label">Minimum item quanity</label>
                      </div>
                    {{/if}}
                    {{#if is_price_based}}
                      {{#price_details}}
                        <div class="group">   
                          <input class="group-input {{#price_title}}filled{{/}}" type="text" name="price_title" required value="{{price_title}}" twoway="false">
                          <span class="bar"></span>
                          <label class="group-label">Title</label>
                        </div>
                        <div class="group">   
                          <input class="group-input {{#amount}}filled{{/}}" type="number" name="amount" required value="{{amount}}" twoway="false">
                          <span class="bar"></span>
                          <label class="group-label">Amount</label>
                        </div>
                        <div class="group">   
                          <p class="field-title filled">Price start date</p>
                          <input type="text" class="group-input date" id="start_date_{{id}}" data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker" name="start_at" value={{start_at}} />
                          <i class="fa fa-calendar calendar-icon"></i>
                        </div>
                        <div class="group">   
                          <p class="field-title filled">Price end date</p>
                          <input type="text" class="group-input date" id="end_date_{{id}}" data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker" name="end_at" value={{end_at}} />
                          <i class="fa fa-calendar calendar-icon"></i>
                        </div>
                      {{/}}
                    {{else}}
                      <div class="group">   
                        <input class="group-input {{#percentage}}filled{{/}}" type="percentage" name="percentage" required value="{{percentage}}" twoway="false">
                        <span class="bar"></span>
                        <label class="group-label">Percentage</label>
                      </div>
                    {{/if}}
                    <div class="group">
                      <p class="field-title filled">Discount applicable items</p>
                      <select id="add-items-{{id}}" name="items" multiple="multiple">
                        {{#items:item}}
                          <option value={{items[item].id}} {{#if is_item_discounted(dp_items, items[item].id)}}selected="selected"{{/if}}>{{items[item].title}}</option>
                        {{/}}
                      </select>
                    </div>
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
                  <form role="form" id="new-coupon-{{id}}"> 
                    <div class="group">   
                      <input class="group-input filled" type="number" name="usage_limit" required min="1" value="1">
                      <span class="bar"></span>
                      <label class="group-label">Usage limit</label>
                    </div>
                    <div class="group">   
                      <input class="group-input filled" type="number" name="count" required min="1" value="1">
                      <span class="bar"></span>
                      <label class="group-label">Number of coupons</label>
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
          </div>
        {{/}}
      </div>
    {{else}}
      <p class="text-center">Currently no discount policies.</p>
    {{/if}}
  </div>
`
