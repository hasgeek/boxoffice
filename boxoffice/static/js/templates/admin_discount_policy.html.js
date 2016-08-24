
export const DiscountPolicyTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <form class="table-title col-sm-4 col-xs-12">
      <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
    </form>
    <div class="table-title col-sm-4 col-sm-offset-4 col-xs-12">
      <button class="boxoffice-button boxoffice-button-action btn-right" on-click="addNewPolicyForm">Create discount policy</button>
    </div>
    {{#show_add_policy_form}}
      <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
        <button on-click="hideNewPolicyForm" class="close-button"><i class="fa fa-close"></i></button>
        <p class="content-slider-title">Add discount policy form</p>
        <div class="content-slider-wrapper">
        </div>
      </div>
    {{/show_order}}
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
                  <p class="content-details">Discount type: {{discount_type}}</p>
                  {{#if discount_type == "Automatic"}}<p class="content-details">Minimum item quanity: {{item_quantity_min}}</p>{{/if}}
                  {{#if is_price_based}}
                    <p class="content-details">Discount: {{currency}}{{discount}}</p>
                  {{else}}
                    <p class="content-details">Discount: {{discount}}%</p>
                  {{/if}}
                  {{#if dp_items}}
                    <p class="content-details">Items:</p>                   
                    <ol class="content-list">
                      {{#dp_items:item}}
                        <li class="content-details">{{dp_items[item].title}}</li>
                      {{/}}
                    </ol>
                  {{/if}}
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
                        <input class="group-input {{#item_quantity_min}}filled{{/}}" type="number" name="item_quantity_min" required value="{{item_quantity_min}}" twoway="false">
                        <span class="bar"></span>
                        <label class="group-label">Minimum item quanity</label>
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
                      <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="editPolicy" {{#editingPolicy}}disabled{{/}}>
                          Update policy
                          {{#editingPolicy}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                      </button>
                      <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hideEditPolicy">Back</button>
                    </div>
                    <p class="error-msg">{{edit_policy_error}}</p>
                  </form>
                </div>
              {{elseif show_add_coupon_form}}
                <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                  <h4 class="text-center form-title">Generate coupon</h4> 
                  <form role="form" id="new-coupon-{{id}}"> 
                    <div class="group">   
                      <input class="group-input {{#title}}filled{{/}}" type="number" name="usage" required value="{{usage}}" twoway="false">
                      <span class="bar"></span>
                      <label class="group-label">Usage limit</label>
                    </div>
                    <div class="btn-wrapper">
                      <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="generateCoupon" {{#generatingCoupon}}disabled{{/}}>
                          Generate
                          {{#generatingCoupon}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                      </button>
                      <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hidegenerateCouponForm">Back</button>
                    </div>
                    <p class="error-msg">{{generate_coupon_error}}</p>
                  </form>
                  {{#if coupons}}
                    <p class="content-details">Recently generated coupons:</p>
                    <p>{{coupons}}</p>
                  {{/if}}
                  {{#coupons:coupon}}
                    <p class="content-details">{{coupon.code}}, usage limit: {{coupon.usage_limit}}</p>
                  {{/}}
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
