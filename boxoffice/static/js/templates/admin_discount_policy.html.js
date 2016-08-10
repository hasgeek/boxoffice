
export const DiscountPolicyTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <form class="table-title col-sm-4 col-xs-12">
      <input autofocus class="form-control" id="filter" type="text" name="key" value="" placeholder="Search"/>
    </form>
    <div class="table-title col-sm-4 col-sm-offset-4 col-xs-12">
      <button class="boxoffice-button boxoffice-button-info add-new-btn" on-click="addPolicy">Create discount policy</button>
    </div>
    {{#if discount_policies}}
      <div class="policies-wrapper">
        {{#discount_policies}}
          <div class="box col-sm-6 col-xs-12">
            <div class="heading">
              <p class="heading-title">{{ title }}</p>
              <div class="heading-edit">
                <button class="edit-btn" on-click="editPolicy(event, event.keypath, true)"><i class="fa fa-edit"></i></button>
              </div>
            </div>
            <div class="content">
              <div class="content-box">
                <p class="content-details">Discount type: {{discount_type}}</p>
                {{#if discount_type == "Automatic"}}<p class="content-details">Minimum item quanity: {{item_quantity_min}}</p>{{/if}}
                {{#if is_price_based}}
                  <p class="content-details">Discount: {{currency}}{{discount}}</p>
                {{else}}
                  <p class="content-details">Discount: {{discount}}%</p>
                {{/if}}
                {{#if items}}
                  <p class="content-details">Items:</p>                   
                  <ol class="content-list">
                    {{#items:item}}
                      <li class="content-details">{{items[item]}}</li>
                    {{/}}
                  </ol>
                {{/if}}
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
