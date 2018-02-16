
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, formErrorHandler, getFormParameters, urlFor, setPageTitle, registerSubmitHandler} from '../models/util.js';
import {itemTemplate} from '../templates/admin_item.html.js';
import {SideBarView} from './sidebar.js';
import {BaseframeForm} from '../models/form_component.js';

export const ItemView = {
  render: function({item_id}={}) {
    const DEFAULT = {
      showForm: true,
      hideForm: false,
      showLoader: true,
      hideLoader: false,
      empty: ""
    };

    fetch({
      url: urlFor('view', {resource: 'item', id: item_id, root: true})
    }).then(function({org_name, org_title, ic_id, ic_title, item, prices, item_form, price_form, discount_policies}) {

      BaseframeForm.defaults.oncomplete = function() {
        let config = Util.getComponentConfig(this);
        let onSuccess = function(remoteData) {
          if (config.action === "edit") {
            //Update the price details
            itemComponent.set('prices.' + config.elementIndex + '.showEditForm', DEFAULT.hideForm);
            itemComponent.set('prices.' + config.elementIndex, remoteData.result.price);
          } else {
            // On creating a new price, add it to prices list
            prices.push(remoteData.result.price);
            itemComponent.hidePriceForm();
          }
        };
        let onError = function(response) {
          let errorMsg;
          errorMsg = formErrorHandler(response, config.formSelector);
          if (config.action === "edit") {
            itemComponent.set('prices.' + config.elementIndex + '.errorMsg', errorMsg);
          } else {
            itemComponent.set('priceForm.errorMsg', errorMsg);
          }
        };
        window.Baseframe.Forms.handleFormSubmit(this.get('url'), `#${this.get('formId')}`, onSuccess, onError, {});
      };

      let itemComponent = new Ractive({
        el: '#main-content-area',
        template: itemTemplate,
        data: {
          item: item,
          prices: prices,
          itemForm: item_form,
          discount_policies: discount_policies,
          priceForm: {
            form: price_form,
            showForm: DEFAULT.hideForm,
            errorMsg: DEFAULT.empty,
          },
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          },
          formatDateTime: function (datetime) {
            return Util.formatDateTime(datetime);
          },
          postUrl: function(action, id) {
            if (action === "edit") {
              return urlFor('edit', { resource: 'price', id: id, root: true});
            }
            return urlFor('new', { scope_ns: 'item', scope_id: item.id, resource: 'price', root: true });
          }
        },
        components: {BaseframeForm: BaseframeForm},
        showPriceForm: function(event, action) {
          if (action === "edit") {
            let price = event.keypath,
              priceId = event.context.id;
            itemComponent.set(price + '.loadingEditForm', DEFAULT.showLoader);
            fetch({
              url: urlFor('edit', { resource: 'price', id: priceId, root: true})
            }).done(({form_template}) => {
              // Set the from baseframe form html as the price's form template
              itemComponent.set(price + '.formTemplate', form_template);
              itemComponent.set(price + '.showForm', DEFAULT.showForm);
              itemComponent.set(price + '.loadingEditForm', DEFAULT.hideLoader);
            }).fail(() => {
              itemComponent.set(price + '.loadingEditForm', DEFAULT.hideLoader);
            })
          } else {
            itemComponent.set('priceForm.showForm', DEFAULT.showForm);
          }
        },
        hidePriceForm: function(event, action) {
          if (action === "edit") {
            itemComponent.set(event.keypath + '.showForm', DEFAULT.hideForm);
          } else {
            itemComponent.set('priceForm.showForm', DEFAULT.hideForm);
          }
        }
      });

      SideBarView.render('items', {org_name, org_title, ic_id, ic_title});
      setPageTitle("Item", item.title);
      NProgress.done();
    });

    window.addEventListener('popstate', (event) => {
      NProgress.configure({ showSpinner: false}).start();
    });
  }
}
