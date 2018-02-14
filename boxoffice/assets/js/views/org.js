
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, formErrorHandler, getFormParameters, urlFor, setPageTitle, registerSubmitHandler} from '../models/util.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js';
import {BaseframeForm} from '../models/form_component.js';

export const OrgView = {
  render: function({org_name}={}) {
    const DEFAULT = {
      showForm: true,
      hideForm: false,
      showLoader: true,
      hideLoader: false,
      empty: ""
    };

    fetch({
      url: urlFor('view', {resource: 'o', id: org_name, root: true})
    }).then(function({id, org_title, item_collections, form}) {

      BaseframeForm.defaults.oncomplete = function() {
        window.Baseframe.Forms.handleAjaxPost(Util.getFormConfig(this, orgComponent.onSuccess, orgComponent.onError));
      };

      let orgComponent = new Ractive({
        el: '#main-content-area',
        template: orgTemplate,
        data: {
          orgName: org_name,
          orgTitle: org_title,
          itemCollections: item_collections,
          icForm: {
            form: form,
            showForm: DEFAULT.hideForm,
            errorMsg: DEFAULT.empty,
          },
          postUrl: function(action, id="") {
            if (action === "edit") {
              return urlFor('edit', { resource: 'ic', id: id, root: true})
            }
            return urlFor('new', { scope_ns: 'o', scope_id: org_name, resource: 'ic', root: true });
          }
        },
        components: {BaseframeForm: BaseframeForm},
        showIcForm: function (event, action) {
          if (action === "edit") {
            let ic = event.keypath,
              icId = event.context.id;
            this.set(ic + '.loadingEditForm', DEFAULT.showLoader);
            fetch({
              url: urlFor('edit', { resource: 'ic', id: icId, root: true})
            }).done(({form_template}) => {
              // Set the from baseframe form html as the item collection's form template
              orgComponent.set(ic + '.formTemplate', form_template);
              orgComponent.set(ic + '.showEditForm', DEFAULT.showForm);
              orgComponent.set(ic + '.loadingEditForm', DEFAULT.hideLoader);
            }).fail(() => {
              orgComponent.set(ic + '.loadingEditForm', DEFAULT.hideLoader);
            })
          } else {
            orgComponent.set('icForm.showAddForm', DEFAULT.showForm);
          }
        },
        hideNewIcForm: function (event) {
          orgComponent.set('icForm.showAddForm', DEFAULT.hideForm);
        },
        viewDashboard: function (url) {
          NProgress.configure({ showSpinner: false}).start();
          //Relative paths(without '/admin') are defined in router.js
          let icViewUrl = url.replace('/admin', '');
          eventBus.trigger('navigate', icViewUrl);
        },
        onSuccess: function(config, remoteData) {
          if (config.action === "edit") {
            //Update the item collection details
            orgComponent.set('itemCollections.' + config.elementIndex + '.showEditForm', DEFAULT.hideForm);
            orgComponent.set('itemCollections.' + config.elementIndex , remoteData.result.item_collection);
          } else {
            // On creating a new item collection, load it's the dashboard.
            orgComponent.viewDashboard(remoteData.result.item_collection.url_for_view);
          }
        },
        onError: function(config, response) {
          let errorMsg;
          errorMsg = formErrorHandler(response, config.formSelector);
          if (config.action === "edit") {
            orgComponent.set('itemCollections.' + config.elementIndex + '.errorMsg', errorMsg);
          } else {
            orgComponent.set('icForm.errorMsg', errorMsg);
          }
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
