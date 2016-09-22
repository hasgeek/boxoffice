export const IndexTemplate = `
  <div class="container">
    <div class="row">
      <h1 class="header">Organizations</h1>
      {{#orgs:org}}
        <div class="box col-sm-6 col-xs-12" id="org-{{ @index }}">
          <div class="heading">
            {{#title}}
              <p class="heading-title">{{ title }}</p>
            {{/title}}
          </div>
          <div class="content">
            <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
              <div class="org-logo"><img src="{{details['logo']}}"/></div>
              <p class="section-title">Organization id</p>
              <p class="section-content">{{id}}</p>
              {{#details:k,v}}
                {{#if k !== 'logo'}}
                  <p class="section-title">{{k}}</p>
                  <div class="section-content">{{{details[k]}}}</div>
                {{/if}}
              {{/details}}
              <p class="section-title">Contact email</p>
              <div class="section-content">{{contact_email}}</div>
              <div class="btn-wrapper">
                <a class="boxoffice-button boxoffice-button-action" href="javascript:void(0)" on-click="navigate">View item collections</a>
              </div>
              {{#infoMsg}}
                <p class="info-msg">{{ infoMsg }} <i class="fa fa-check"></i></p>
              {{/}}
            </div>
        </div>
      {{/orgs}}
    </div>
  </div>
`
