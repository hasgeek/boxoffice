export const orgTemplate = `
  <div class="container">
    <div class="row">
      <h1 class="header">{{ title }}</h1>
      {{#item_collections:item_collection}}
        <div class="box col-sm-6 col-xs-12" id="item-collection-{{ @index }}">
          <div class="heading">
            {{#title}}
              <p class="heading-title">{{ title }}</p>
            {{/title}}
          </div>
          <div class="content">
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <p class="section-title">Item collection id</p>
              <p class="section-content">{{id}}</p>
              <p class="section-title">Item collection description</p>
              <div class="section-content">{{{description_html}}}</div>
              <div class="btn-wrapper">
                <a class="boxoffice-button boxoffice-button-action" href="javascript:void(0)" on-click="navigate">View {{title}} dashboard</a>
              </div>
              {{#infoMsg}}
                <p class="info-msg">{{ infoMsg }} <i class="fa fa-check"></i></p>
              {{/}}
            </div>
        </div>
      {{/item_collections}}
    </div>
  </div>
`
