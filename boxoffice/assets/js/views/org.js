
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, formErrorHandler, getFormParameters, urlFor, setPageTitle, registerSubmitHandler} from '../models/util.js';
import {orgTemplate} from '../templates/org.html.js';
import {SideBarView} from './sidebar.js'

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
      let ICForm = Ractive.extend({
        isolated: false,
        template: function(data) {
          if(this.get('formTemplate')) {
            // Add ractive on click event handler to the baseframe form
            return Util.getFormTemplate(this.get('formTemplate'), 'onFormSubmit(event, "edit")');
          }
          return Util.getFormTemplate(form, 'onFormSubmit(event, "new")');
        },
        computed: {
          formId: {
            get: function() {
              if(this.get('formTemplate')) {
                return Util.getElementId(this.get('formTemplate'));
              }
              return Util.getElementId(form);
            }
          }
        },
        onFormSubmit: function(event, action) {
          event.original.preventDefault();
          let formSelector = '#' + this.get('formId'),
            url = action === "edit" ? urlFor('edit', { resource: 'ic', id: this.get('icId'), root: true}) :
                  urlFor('new', { scope_ns: 'o', scope_id: org_name, resource: 'ic', root: true }),
            ic = action === "edit" ? 'item_collections.' + this.get('ic') : '';

          post({
            url: url,
            data: getFormParameters(formSelector),
            formId: formSelector
          }).done((remoteData) => {
            if (action === "edit") {
              //Update the item collection details
              orgComponent.set(ic + '.showEditForm', DEFAULT.hideForm);
              orgComponent.set(ic, remoteData.result.item_collection);
            } else {
              // On creating a new item collection, load it's the dashboard.
              orgComponent.viewDashboard(remoteData.result.item_collection.url_for_view);
            }
          }).fail((response) => {
            let errorMsg;
            errorMsg = formErrorHandler(response, this.get('formId'));
            orgComponent.set(ic + '.errorMsg', errorMsg);
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
          showAddForm: DEFAULT.hideForm,
        },
        components: {ICForm: ICForm},
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
            this.set('showAddForm', DEFAULT.showForm);
          }
        },
        hideNewIcForm: function (event) {
          this.set('showAddForm', DEFAULT.hideForm);
        },
        viewDashboard: function (url) {
          NProgress.configure({ showSpinner: false}).start();
          //Relative paths(without '/admin') are defined in router.js
          let icViewUrl = url.replace('/admin', '');
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
