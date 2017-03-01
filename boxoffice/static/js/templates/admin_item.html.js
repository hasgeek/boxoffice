
export const ItemTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <div class="title-wrapper col-sm-4 col-xs-12">
      <input type="text" autofocus class="form-control" placeholder="Search discount policy" value="{{searchText}}" />
      {{#searchText}}<a on-click="clearSearchField()" class="clear-field"><i class="fa fa-close"></i></a>{{/}}
    </div>

    {{#if items}}
      <div class="policies-wrapper">
        {{#items}}
          <div class="box col-sm-6 col-xs-12" id="item-{{id}}">
            <div class="heading">
              <p class="heading-title">{{ title }}</p>
            </div>
            <div class="content">
              {{#if !showPolicyForm && !showCouponForm}}
                <div class="content-box">
                  <p class="content-details"><b>Category:</b></p>
                  <p class="content-details-text">{{ category }}</p>

                  <p class="content-details"><b>Current price:</b></p>
                  {{#if current_price}}
                    <p class="content-details-text">{{ formatCurrency(current_price) }}</p>
                  {{else}}
                    <p class="content-details-text">No current price</p>
                  {{/if}}

                  {{#if current_price}}
                    <p class="content-details"><b>Price ends on:</b></p>
                    <p class="content-details-text">{{ price_valid_upto }}</p>
                  {{/if}}

                  <p class="content-details"><b>Discount policies applicable:</b></p>
                  <ol class="content-list">
                  {{#discount_policies}}
                    <li class="content-details">{{ . }}</li>
                  {{/}}
                  </ol>

                </div>
              
              {{/if}}
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
      <p class="text-center">Currently no items.</p>
    {{/if}}
  </div>
`
