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
          <ICForm></ICForm>
          <p class="error-msg">{{{ icForm.errorMsg }}}</p>
        </div>
      </div>
    {{/if}}
    {{#item_collections:item_collection}}
      <div class="box col-sm-6 col-xs-12" id="item-collection-{{ @index }}">
        <div class="heading">
          {{#title}}
            <p class="heading-title">{{ title }}</p>
          {{/title}}
          <div class="heading-edit">
            <button class="edit-btn" on-click="showEditICForm(event)"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>
          </div>
        </div>
        <div class="content">
          {{#if showEditForm}}
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <EditICForm formTemplate="{{ formTemplate }}" ic="{{ item_collection }}" icId="{{ id }}"></EditICForm>
              <p class="error-msg">{{{ errorMsg }}}</p>
            </div>
          {{else}}
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <p class="section-title">Item collection id</p>
              <p class="section-content">{{ id }}</p>
              <p class="section-title">Item collection description</p>
              <div class="section-content">{{{ description }}}</div>
              <div class="btn-wrapper">
                <a class="boxoffice-button boxoffice-button-action" href="/{{ orgName }}/{{ name }}">View listing</a>
                <a class="boxoffice-button boxoffice-button-action" href="javascript:void(0)" on-click="viewDashboard(event)">View dashboard</a>
              </div>
            </div>
          {{/if}}
        </div>
      </div>
    {{/item_collections}}
  </div>
`
