export const orgTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ orgTitle }}</h1>
    <div class="title-wrapper col-xs-12">
      <button class="boxoffice-button boxoffice-button-action btn-right" on-click="showNewIcForm(event)">Create new item collection</button>
    </div>
    {{#if showAddForm}}
      <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
        <button on-click="hideNewIcForm(event)" class="close-button"><i class="fa fa-close"></i></button>
        <p class="content-slider-title">Add a new item collection</p>
        <div class="content-slider-wrapper">
          <AddICFormComponent></AddICFormComponent>
          <p class="error-msg">{{{ newIC.errorMsg }}}</p>
        </div>
      </div>
    {{/if}}
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
              <a class="boxoffice-button boxoffice-button-action" href="/{{orgName}}/{{name}}">View listing</a>
              <a class="boxoffice-button boxoffice-button-action" href="javascript:void(0)" on-click="navigate">View dashboard</a>
            </div>
            {{#infoMsg}}
              <p class="info-msg">{{ infoMsg }} <i class="fa fa-check"></i></p>
            {{/}}
          </div>
      </div>
    {{/item_collections}}
  </div>
`
