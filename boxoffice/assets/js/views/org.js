
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {fetch, urlFor, setPageTitle} from '../models/util.js';
import {SideBarView} from './sidebar.js';

const orgTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ orgTitle }}</h1>
    <div class="title-wrapper col-xs-12">
      <a class="boxoffice-button boxoffice-button-action btn-right" href="/admin/o/{{orgName}}/ic/new" data-navigate>
        New item collection
      </a>
    </div>
    {{#itemCollections:ic}}
      <div class="box col-sm-6 col-xs-12" id="item-collection-{{ @index }}">
        <div class="heading">
          {{#title}}
            <p class="heading-title">{{ title }}</p>
          {{/title}}
        </div>
        <div class="content">
          <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
            <p class="section-title">Item collection id</p>
            <p class="section-content">{{ id }}</p>
            <p class="section-title">Item collection description</p>
            <div class="section-content">{{{ description }}}</div>
            <div class="btn-wrapper">
              <a class="boxoffice-button boxoffice-button-action" href="/{{ orgName }}/{{ name }}">View listing</a>
              <a class="boxoffice-button boxoffice-button-action" href="/admin/ic/{{id}}" data-navigate>View dashboard</a>
            </div>
          </div>
        </div>
      </div>
    {{/itemCollections}}
  </div>
`

export const OrgView = {
  render: function({org_name}={}) {
    fetch({
      url: urlFor('view', {resource: 'o', id: org_name, root: true})
    }).then(function({id, org_title, item_collections, form}) {
      let orgComponent = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          orgName: org_name,
          orgTitle: org_title,
          itemCollections: item_collections
        }
      });

      SideBarView.render('org', {org_name, org_title});
      setPageTitle(org_title);
      NProgress.done();
    });
  }
}
