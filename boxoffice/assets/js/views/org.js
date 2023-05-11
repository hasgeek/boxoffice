/* eslint-disable no-unused-vars */
import { navigateTo } from './navigate';

import { fetch, urlFor, setPageTitle } from '../models/util';
import { SideBarView } from './sidebar';

const Ractive = require('ractive');
const NProgress = require('nprogress');

const orgTemplate = `
  <div class="content-wrapper clearfix">
    <h1 class="header col-xs-12">{{ accountTitle }}</h1>
    <div class="title-wrapper col-xs-12 col-md-4">
      <form class="search-form" id='order-jump-form' method='post'>
        <input type="text" autofocus size="30" class="form-control icon-placeholder order-jump-input" id="order-receipt-no-input" placeholder="&#xF002; Search order with receipt no." />
      </form>
    </div>
    <div class="title-wrapper col-xs-12 col-md-8">
      <a class="boxoffice-button boxoffice-button-action btn-right" href="/admin/o/{{accountName}}/menu/new" data-navigate>
        New item collection
      </a>
    </div>
    {{#menus:menu}}
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
            <div class="section-content">{{{ description.html }}}</div>
            <div class="btn-wrapper">
              <a class="boxoffice-button boxoffice-button-info" href="/{{ accountName }}/{{ name }}">View listing</a>
              <a class="boxoffice-button boxoffice-button-primary" href="/admin/menu/{{id}}" data-navigate>View dashboard</a>
            </div>
          </div>
        </div>
      </div>
    {{/menus}}
  </div>
`;

export const OrgView = {
  render({ accountName } = {}) {
    fetch({
      url: urlFor('view', { resource: 'o', id: accountName, root: true }),
    }).then(({ id, title: accountTitle, menus, form }) => {
      const orgComponent = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          accountName,
          accountTitle,
          menus,
        },
      });

      $('#order-jump-form').submit((submitEvt) => {
        submitEvt.preventDefault();
        const orderReceiptNo = $('#order-receipt-no-input').val();
        navigateTo(`/admin/o/${accountName}/order/${orderReceiptNo}`);
      });

      SideBarView.render('org', {
        accountName,
        accountTitle,
      });
      setPageTitle(accountTitle);
      NProgress.done();
    });
  },
};

export { OrgView as default };
