export const orgTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ orgTitle }}</h1>
    <div class="title-wrapper col-xs-12">
      <button class="boxoffice-button boxoffice-button-action btn-right" on-click="showIcForm(event, 'new')">Create new item collection</button>
    </div>
    {{#if icForm.showAddForm}}
      <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
        <button on-click="hideNewIcForm(event)" class="close-button"><i class="fa fa-close"></i></button>
        <p class="content-slider-title">Add a new item collection</p>
        <div class="content-slider-wrapper">
          <BaseframeForm formTemplate="{{ icForm.form }}" index="" action="new" url="{{ postUrl('new') }}"></BaseframeForm>
          <p class="error-msg">{{{ icForm.errorMsg }}}</p>
        </div>
      </div>
    {{/if}}
    {{#itemCollections:ic}}
      <div class="box col-sm-6 col-xs-12" id="item-collection-{{ @index }}">
        <div class="heading">
          {{#title}}
            <p class="heading-title">{{ title }}</p>
          {{/title}}
          <div class="heading-edit">
            <button class="edit-btn" on-click="showIcForm(event, 'edit')"><i class="fa fa-edit"></i>{{#loadingEditForm}}<i class="fa fa-spinner fa-spin">{{/}}</button>
          </div>
        </div>
        <div class="content">
          {{#if showEditForm}}
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <BaseframeForm formTemplate="{{ formTemplate }}" index="{{ @index }}" action="edit" url="{{ postUrl('edit', id) }}"></BaseframeForm>
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
                <a class="boxoffice-button boxoffice-button-action" href="javascript:void(0)" on-click="viewDashboard(url_for_view)">View dashboard</a>
              </div>
            </div>
          {{/if}}
        </div>
      </div>
    {{/itemCollections}}
  </div>
`
