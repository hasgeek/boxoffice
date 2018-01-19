
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, getFormParameters, urlFor, setPageTitle} from '../models/util.js';
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
      let AddICFormComponent = Ractive.extend({
        isolated: false,
        template: Util.getFormTemplate(form),
        data: {
          addFormId: Util.getElementId(form),
        },
        onFormSubmit: function(event) {
          event.original.preventDefault();
          let self = this;
          let formSelector = '#' + self.get('addFormId');
          self.set('formOnSubmit', true);
          post({
            url: urlFor('new', {
              scope_ns: 'o',
              scope_id: org_name,
              resource: 'ic',
              root: true
            }),
            processData: false,
            data: getFormParameters(formSelector)
          }).done((remoteData) => {
            self.set('formOnSubmit', false);
            orgComponent.unshift('item_collections', remoteData.result.item_collection);
            orgComponent.hideNewIcForm();
          }).fail(function (response) {
            self.set('formOnSubmit', false);
            let errorMsg = DEFAULT.empty;
            if (response.readyState === 4) {
              if (response.status === 500) {
                errorMsg = "Internal Server Error";
              } else {
                Util.showFormErrors(self.get('addFormId'), response.responseJSON.errors);
              }
            } else {
              errorMsg = "Unable to connect. Please try again.";
            }
            orgComponent.set('newIC.errorMsg', errorMsg);
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
          newIC: '',
          showAddForm: DEFAULT.hideForm,
          formOnSubmit: DEFAULT.hideLoader
        },
        components: {AddICFormComponent: AddICFormComponent},
        showNewIcForm: function(event) {
          this.set('showAddForm', DEFAULT.showForm);
        },
        hideNewIcForm: function (event) {
          this.set('showAddForm', DEFAULT.hideForm);
        }
      });

      SideBarView.render('org', {org_name, org_title});
      setPageTitle(org_title);
      NProgress.done();

      orgComponent.on('navigate', function(event, method){
        NProgress.configure({ showSpinner: false}).start();
        eventBus.trigger('navigate', event.context.url);
      });
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false}).start();
    });
  }
}
