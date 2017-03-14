
export const DiscountPolicyTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <div class="title-wrapper col-sm-4 col-xs-12">
      <input type="text" autofocus class="form-control" placeholder="Search discount policy" value="{{searchText}}" />
      {{#searchText}}<a on-click="clearSearchField()" class="clear-field"><i class="fa fa-close"></i></a>{{/}}
    </div>
    <div class="title-wrapper col-sm-4 col-sm-offset-4 col-xs-12">
      <button class="boxoffice-button boxoffice-button-action btn-right" on-click="showNewPolicyForm(event)">Create discount policy</button>
    </div>
    {{#if showAddPolicyForm}}
      <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
        <button on-click="hideNewPolicyForm(event)" class="close-button"><i class="fa fa-close"></i></button>
        <p class="content-slider-title">Add a new discount policy</p>
        <div class="content-slider-wrapper">
          <form role="form" id="new-policy-form" name="adding-new-policy-form">
            <div class="group">
              <input type="text" name="title" value="{{newDiscountPolicy.title}}" class="group-input {{#newDiscountPolicy.title}}filled{{/}}" />
              <span class="bar"></span>
              <label class="group-label">Title</label>
              {{#newDiscountPolicy.errormsg.title}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.title }}</p>{{/}}
            </div>

            <div class="group">
              <p class="field-title filled">What type of discount?</p>
              <label class="radio-inline">
                <input type="radio" name="is_price_based" value=1 on-click="onPolicyChange(event)" checked />
                Special price
              </label>
              <label class="radio-inline">
                <input type="radio" name="is_price_based" value=0 on-click="onPolicyChange(event)" />
                Percentage
              </label>
            </div>

            {{#if newDiscountPolicy.is_price_based == 0}}
              <div class="group">
                <p class="field-title filled">How is this discount going to be availed?</p>
                <label class="radio-inline">
                  <input type="radio" name="discount_type" value=1 on-click="onPolicyTypeChange(event)" checked />
                  Coupon based
                </label>
                  <label class="radio-inline">
                    <input type="radio" name="discount_type" value=0 on-click="onPolicyTypeChange(event)" />
                    Automatic
                  </label>
              </div>
            {{/if}}

            {{#if newDiscountPolicy.discount_type == 0}}
              <div class="group">   
                <input type="number" name="item_quantity_min" value={{ newDiscountPolicy.item_quantity_min }} class="group-input {{#newDiscountPolicy.item_quantity_min}}filled{{/}}" />
                <span class="bar"></span>
                <label class="group-label">Minimum number of tickets</label>
                {{#newDiscountPolicy.errormsg.item_quantity_min}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.item_quantity_min }}</p>{{/}}
              </div>
              <p class="form-help-text">For Automatic discounts, minimum number of tickets user needs to buy to avail this discount.<br>Eg:- '5% discount on buying 5 or more tickets.'</p>
            {{else}}
              <div class="group">
                <input type="text" name="discount_code_base" value="{{ newDiscountPolicy.discount_code_base }}" class="group-input {{#newDiscountPolicy.discount_code_base}}filled{{/}}" />
                <span class="bar"></span>
                <label class="group-label">Discount code base</label>
                {{#newDiscountPolicy.errormsg.discount_code_base}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.discount_code_base }}</p>{{/}}
              </div>
              <p class="form-help-text">Discount code base is for generating coupons in bulk<br>Eg:- 'hasgeek-volunteer'</p>

              <div class="group">
                <input type="number" name="bulk_coupon_usage_limit" value="{{ newDiscountPolicy.bulk_coupon_usage_limit }}" class="group-input {{#newDiscountPolicy.discount_code_base}}filled{{/}}"/>
                <span class="bar"></span>
                <label class="group-label">Usage limit of each bulk coupon</label>
                {{#newDiscountPolicy.errormsg.bulk_coupon_usage_limit}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.bulk_coupon_usage_limit }}</p>{{/}}
              </div>
              <p class="form-help-text">Specify the number of times each bulk coupon can be used</p>
            {{/if}}

            {{#if newDiscountPolicy.is_price_based == 1}}
              <div class="group">
                <input type="number" name="amount" value={{ newDiscountPolicy.amount }} class="group-input {{#newDiscountPolicy.amount}}filled{{/}}" />
                <span class="bar"></span>
                <label class="group-label">Special price amount</label>
                {{#newDiscountPolicy.errormsg.amount}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.amount }}</p>{{/}}
              </div>
              <div class="group inline-group clearfix">
                <div class="input-group">
                  <p class="field-title filled">Special price start date</p>
                  <input name="start_at" value="{{ newDiscountPolicy.start_at }}" class="group-input date" id="start-date" />
                  <i class="fa fa-calendar calendar-icon"></i>
                  {{#newDiscountPolicy.errormsg.start_at}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.start_at }}</p>{{/}}
                </div>
                <div class="input-group">
                  <p class="field-title filled">Special price end date</p>
                  <input name="end_at" value="{{newDiscountPolicy.end_at}}" class="group-input date" id="end-date" />
                  <i class="fa fa-calendar calendar-icon"></i>
                  {{#newDiscountPolicy.errormsg.end_at}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.end_at }}</p>{{/}}
                </div>
              </div>
              <div class="group clearfix">
                <p class="field-title filled clearfix">What is the discount for?</p>
                <select name="item" id="add-item" class="items-select2">
                </select>
                {{#newDiscountPolicy.errormsg.items}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.items }}</p>{{/}}
              </div>
            {{else}}
              <div class="group">
                <input type="number" name="percentage" value={{ newDiscountPolicy.percentage }} class="group-input {{#newDiscountPolicy.percentage}}filled{{/}}" />
                <span class="bar"></span>
                <label class="group-label">Discount percentage</label>
                {{#newDiscountPolicy.errormsg.percentage}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.percentage }}</p>{{/}}
              </div>
              <p class="field-title filled">What is the discount for?</p>
              <div class="group">
                <select name="items" id="add-items" multiple class="items-select2">
                </select>
                {{#newDiscountPolicy.errormsg.items}}<p class="form-error-msg">{{ newDiscountPolicy.errormsg.items }}</p>{{/}}
              </div>
            {{/if}}

            <input type="hidden" name="csrf_token" value="{{ getCsrfToken() }}" />

            <div class="btn-wrapper">
              <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hideNewPolicyForm(event)">Back</button>
              <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="addNewPolicy(event)" {{#newDiscountPolicy.creatingPolicy}}disabled{{/}}>
                Create policy
                {{#newDiscountPolicy.creatingPolicy}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
              </button>
            </div>
            <p class="error-msg">{{{ newDiscountPolicy.errorMsg }}}</p>
          </form>
        </div>
      </div>
    {{/if}}

    {{#if discountPolicies}}
      <div class="policies-wrapper">
        {{#discountPolicies}}
          <div class="box col-sm-6 col-xs-12" id="dp-{{id}}">
            <div class="heading">
              <p class="heading-title">{{ title }}</p>
              <div class="heading-edit">
                {{#if !showPolicyForm && !showCouponForm}}<button class="edit-btn" on-click="showEditPolicyForm(event)"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>{{/if}}
              </div>
            </div>
            <div class="content">
              {{#if !showPolicyForm && !showCouponForm}}
                <div class="content-box">
                  <p class="content-details"><b>Discount type:</b></p>
                  <p class="content-details-text">{{ discount_type }}</p>

                  {{#if is_price_based}}
                    <p class="content-details"><b>Discounted price:</b></p>
                    <p class="content-details-text">{{ currency }}{{ price_details.amount }}</p>
                  {{else}}
                    <p class="content-details"><b>Discount in percentage:</b></p>
                    <p class="content-details-text">{{ discount }}%</p>
                  {{/if}}

                  {{#if discount_type == "Automatic"}}
                    <p class="content-details"><b>Minimum number of a particular item that needs to be <br>bought for this discount to apply:</b></p>
                    <p class="content-details-text">{{ item_quantity_min }}</p>
                  {{else}}
                    {{#if discount_code_base}}
                      <p class="content-details"><b>Discount code base:</b></p>
                      <p class="content-details-text">{{ discount_code_base }}</p>
                    {{/if}}
                      <p class="content-details"><b>Number of times each bulk coupon can be used:</b></p>
                      <p class="content-details-text">{{ bulk_coupon_usage_limit }}</p>
                  {{/if}}

                  {{#if dp_items}}
                    <p class="content-details"><b>This discount policy applies to:</b></p>
                    <ol class="content-list">
                      {{#dp_items:item}}
                        <li class="content-details">{{ dp_items[item].title }}</li>
                      {{/}}
                    </ol>
                  {{/if}}

                  {{#if discount_type == "Coupon based"}}
                    <button class="boxoffice-button boxoffice-button-action btn-right" on-click="getCouponList(event)">
                      List coupons{{#loadingCoupons}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                    </button>
                    <button class="boxoffice-button boxoffice-button-action btn-right btn-inline" on-click="showCouponForm(event)">Generate coupon</button>
                    <p class="error-msg">{{{ loadingCouponErrorMsg }}}</p>
                  {{/if}}
                </div>
              {{elseif showPolicyForm}}
                <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                  <h4 class="text-center form-title">Edit</h4>   
                  <form role="form" id="policy-form-{{ id }}" name="edit-policy-form-{{ id }}">
                    <input type="hidden" name="discount_policy_id" value="{{ id }}" />
                    <div class="group">   
                      <input type="text" name="title" value="{{ title }}" twoway="false" class="group-input {{#title}}filled{{/}}" />
                      <span class="bar"></span>
                      <label class="group-label">Title</label>
                      {{#errormsg.title}}<p class="form-error-msg">{{ errormsg.title }}</p>{{/}}
                    </div>

                    {{#if is_price_based}}
                      <input type="hidden" name="is_price_based" value=1 />
                      {{#price_details}}
                        <div class="group">   
                          <input type="text" name="amount" value="{{ amount }}" twoway="false" class="group-input {{#amount}}filled{{/}}" />
                          <span class="bar"></span>
                          <label class="group-label">Amount</label>
                          {{#errormsg.amount}}<p class="form-error-msg">{{ errormsg.amount }}</p>{{/}}
                        </div>
                        <div class="group">
                          <p class="field-title filled">Price start date</p>
                          <input type="text" name="start_at" value="{{ start_at }}" twoway="false" class="group-input date" id="start-date-{{ id }}" />
                          <i class="fa fa-calendar calendar-icon"></i>
                          {{#errormsg.start_at}}<p class="form-error-msg">{{ errormsg.start_at }}</p>{{/}}
                        </div>
                        <div class="group">
                          <p class="field-title filled">Price end date</p>
                          <input type="text" name="end_at" value="{{ end_at }}" twoway="false" class="group-input date" id="end-date-{{ id }}" />
                          <i class="fa fa-calendar calendar-icon"></i>
                          {{#errormsg.end_at}}<p class="form-error-msg">{{ errormsg.end_at }}</p>{{/}}
                        </div>

                      {{/}}
                    {{else}}
                      <input type="hidden" name="is_price_based" value=0 />
                      <div class="group">   
                        <input type="number" name="percentage" value="{{ percentage }}" twoway="false" class="group-input {{#percentage}}filled{{/}}" />
                        <span class="bar"></span>
                        <label class="group-label">Percentage</label>
                        {{#errormsg.percentage}}<p class="form-error-msg">{{ errormsg.percentage }}</p>{{/}}
                      </div>

                    {{/if}}

                    {{#if discount_type == "Automatic"}}
                      <input type="hidden" name="discount_type" value=0 />
                      <div class="group">   
                        <input type="number" name="item_quantity_min" value="{{ item_quantity_min }}" twoway="false" class="group-input {{#item_quantity_min}}filled{{/}}" />
                        <span class="bar"></span>
                        <label class="group-label">Minimum item quanity</label>
                        {{#errormsg.item_quantity_min}}<p class="form-error-msg">{{ errormsg.item_quantity_min }}</p>{{/}}
                      </div>
                    {{else}}
                      <input type="hidden" name="discount_type" value=1 />
                      <div class="group">   
                        <input type="text" name="discount_code_base" value="{{ discount_code_base }}" twoway="false" class="group-input {{#discount_code_base}}filled{{/}}" />
                        <span class="bar"></span>
                        <label class="group-label">Discount coupon prefix</label>
                        {{#errormsg.discount_code_base}}<p class="form-error-msg">{{ errormsg.discount_code_base }}</p>{{/}}
                      </div>
                      <p class="form-help-text">Discount coupon prefix is for generating bulk coupons<br>Eg:- 'hasgeek-volunteer'</p>
                      <div class="group">   
                        <input type="number" name="bulk_coupon_usage_limit" value="{{ bulk_coupon_usage_limit }}" twoway="false" class="group-input {{#bulk_coupon_usage_limit}}filled{{/}}" />
                        <span class="bar"></span>
                        <label class="group-label">Number of times each bulk coupon can be used</label>
                        {{#errormsg.bulk_coupon_usage_limit}}<p class="form-error-msg">{{ errormsg.item_quantity_min }}</p>{{/}}
                      </div>
                    {{/if}}

                    <p class="field-title filled">What is the discount for?</p>
                    <div class="group"> 
                      <select {{#if is_price_based}}name="item" id="add-item-{{ id }}"{{else}}name="items" id="add-items-{{ id }}" multiple{{/if}} class="items-select2">
                        {{#dp_items:item}}
                          <option value="{{ dp_items[item].id }}" selected title="{{ dp_items[item].title }}">{{ dp_items[item].title }}</option>
                        {{/}}
                      </select>
                      {{#errormsg.items}}<p class="form-error-msg">{{ errormsg.items }}</p>{{/}}
                    </div>

                    <input type="hidden" name="csrf_token" value="{{ getCsrfToken() }}" />

                    <div class="btn-wrapper">
                      <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hideEditPolicyForm(event)">Back</button>
                      <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="editPolicy(event)" {{#editingPolicy}}disabled{{/}}>
                          Update policy
                          {{#editingPolicy}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                      </button>
                    </div>
                    <p class="error-msg">{{{ errorMsg }}}</p>
                  </form>
                </div>
              {{elseif showCouponForm}}
                <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
                  <h4 class="text-center form-title">Generate coupon</h4>
                  <form role="form" id="new-coupon-{{ id }}" name="generate-coupon-form-{{ id }}">
                    <div class="group">   
                      <input type="number" name="count" value="{{ .count }}" class="group-input {{#count}}filled{{/}}" />
                      <span class="bar"></span>
                      <label class="group-label">How many coupons?</label>
                      {{#errormsg.count}}<p class="form-error-msg">{{ errormsg.count }}</p>{{/}}
                    </div>

                    {{#if count == 1}}
                      <div class="group">   
                        <input type="text" name="code" value="{{ .coupon_code }}" class="group-input {{#coupon_code}}filled{{/}}" />
                        <span class="bar"></span>
                        <label class="group-label">What coupon code?</label>
                      </div>
                      <p class="form-help-text">Eg: Hasjob</p>
                      <div class="group">
                        <input type="number" name="usage_limit" value="1" class="group-input filled" />
                        <span class="bar"></span>
                        <label class="group-label">How many times can each coupon be used?</label>
                        {{#errormsg.usage_limit}}<p class="form-error-msg">{{ errormsg.usage_limit }}</p>{{/}}
                      </div>
                    {{else}}
                      <div class="group">   
                        <input type="text" name="discount_code_base" value="{{ discount_code_base }}" class="group-input {{#discount_code_base}}filled{{/}}" readonly="readonly" />
                        <span class="bar"></span>
                        <label class="group-label">Discount coupon prefix</label>
                      </div>
                      {{#errormsg.discount_code_base}}<p class="form-error-msg">{{ errormsg.discount_code_base }}</p>{{/}}
                      <div class="group">   
                        <input type="text" name="bulk_coupon_usage_limit" value="{{ bulk_coupon_usage_limit }}" class="group-input {{#bulk_coupon_usage_limit}}filled{{/}}" readonly="readonly" />
                        <span class="bar"></span>
                        <label class="group-label">Number of times each bulk coupon can be used</label>
                      </div>
                      {{#errormsg.bulk_coupon_usage_limit}}<p class="form-error-msg">{{ errormsg.bulk_coupon_usage_limit }}</p>{{/}}
                    {{/if}}

                    <input type="hidden" name="csrf_token" value="{{ getCsrfToken() }}" />

                    <div class="btn-wrapper">
                      <button type="button" class="boxoffice-button boxoffice-button-info" on-click="hideCouponForm(event)">Back</button>
                      <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="generateCoupon(event)" {{#generatingCoupon}}disabled{{/}}>
                          Generate
                          {{#generatingCoupon}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                      </button>
                    </div>
                    <p class="error-msg">{{{ generateCouponErrorMsg }}}</p>
                  </form>
                </div>
              {{/if}}
            </div>

            <div class="modal" id="list-coupons-{{ id }}" tabindex="-1" role="dialog">
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title">Discount Coupons</h4>
                  </div>
                  <div class="modal-body clearfix">
                   {{#if coupons}}
                      <button class="boxoffice-button boxoffice-button-action btn-right copy-coupons-list" data-clipboard-target="#coupons-list-{{id}}">Copy to clipboard</button>
                      <form class="title-wrapper col-sm-4 col-xs-6">
                        <input autofocus class="form-control" id="filter-{{ id }}" type="text" name="key" value="" placeholder="Search coupon" />
                      </form>
                      <div class="col-xs-12">
                        <table class="table table-hover stats-table table-orders footable toggle-circle-filled" id="coupons-list-{{ id }}" data-filter="#filter-{{ id }}">
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
                </div>
              </div>
            </div>

            <div class="modal" id="generated-coupons-{{ id }}" tabindex="-1" role="dialog">
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title">{{ title }}</h4>
                  </div>
                  <div class="modal-body">
                    <div class="group group-margin-top">
                      <input type="text" value="{{ event_url }}" class="group-input {{#event_url}}filled{{/}}"/>
                      <span class="bar"></span>
                      <label class="group-label">Event website url</label>
                    </div>
                    <p class="form-help-text">Eg:- https://jsfoo.in/2016</p>
                    <p class="pull-left">Here are the discount coupons:</p>
                    <button class="boxoffice-button boxoffice-button-action btn-right copy-coupons" data-clipboard-target="#new-coupons-{{ id }}">Copy discount coupons to clipboard</button>
                    <table class="table table-orders" id="new-coupons-{{ id }}">
                      <tbody>
                      {{#coupons}}
                        <tr>
                          {{#if event_url }}
                            <td>{{ event_url }}?code={{ . }}</td>
                          {{else}}
                            <td>{{ . }}</td>
                          {{/if}}
                        </tr>
                      {{/}}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

          </div>
        {{/}}
        {{#if paginated}}
        <div class="text-center">
          <nav aria-label="Page navigation">
            <ul class="pagination">
              <li>
                {{#if currentPage == 1}}
                  <a href="#" on-click="paginate(event, 1)" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                {{else}}
                  <a href="#" on-click="paginate(event, currentPage - 1)" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                {{/if}}
              </li>
              {{#pages:index}}
              <li {{#if currentPage == pages[index]}}class="active"{{/if}} ><a href="#" on-click="paginate(event, pages[index])">{{pages[index]}}</a></li>
              {{/}}
              <li>
                {{#if currentPage == totalPages}}
                  <a href="#" on-click="paginate(event, totalPages)" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                {{else}}
                  <a href="#" on-click="paginate(event, currentPage + 1)" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                {{/if}}
              </li>
            </ul>
          </nav>
        </div>
        {{/if}}
      </div>
    {{else}}
      <p class="text-center">Currently no discount policies.</p>
    {{/if}}
  </div>
`
