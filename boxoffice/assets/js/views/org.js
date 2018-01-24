
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, formErrorHandler, getFormParameters, urlFor, setPageTitle} from '../models/util.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

export const OrgView = {
  render: function({org_name}={}) {
    const DEFAULT = {
      showForm: true,
      hideForm: false,
      empty: ""
    };

    fetch({
      url: urlFor('view', {resource: 'o', id: org_name, root: true})
    }).then(function({id, org_title, item_collections, form}) {
      let ICForm = Ractive.extend({
        isolated: false,
        template: Util.getFormTemplate(form, 'onFormSubmit(event)'),
        data: {
          formId: Util.getElementId(form),
          formSubmit: DEFAULT.btnEnable
        },
        onFormSubmit: function(event) {
          event.original.preventDefault();
          let formSelector = '#' + this.get('formId');
          post({
            url: urlFor('new', {
              scope_ns: 'o',
              scope_id: org_name,
              resource: 'ic',
              root: true
            }),
            data: getFormParameters(formSelector),
            formId: formSelector
          }).done((remoteData) => {
            NProgress.configure({ showSpinner: false}).start();
            let newICUrl = remoteData.result.item_collection.url_for_view.replace('/admin', '');
            eventBus.trigger('navigate', newICUrl);
          }).fail((response) => {
            let errorMsg;
            errorMsg = formErrorHandler(response, this.get('formId'));
            orgComponent.set('icForm.errorMsg', errorMsg);
          });
        }
      });

      let orgComponent = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          orgName: org_name,
          orgTitle: org_title,
          item_collections: item_collections,
          icForm: '',
          showAddForm: DEFAULT.hideForm
        },
        components: {ICForm: ICForm},
        showNewIcForm: function (event) {
          this.set('showAddForm', DEFAULT.showForm);
        },
        hideNewIcForm: function (event) {
          this.set('showAddForm', DEFAULT.hideForm);
        },
        viewDashboard: function (event) {
          NProgress.configure({ showSpinner: false}).start();
          //Relative paths(without '/admin') are defined in router.js
          let icViewUrl = event.context.url_for_view.replace('/admin', '');
          eventBus.trigger('navigate', icViewUrl);
        }
      });

      SideBarView.render('org', {org_name, org_title});
      setPageTitle(org_title);
      NProgress.done();
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false}).start();
    });
  }
}
