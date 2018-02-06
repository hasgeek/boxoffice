
var Ractive = require('ractive');
import {eventBus} from './main_admin.js'
var NProgress = require('nprogress');
import {Util, fetch, post, formErrorHandler, getFormParameters, urlFor, setPageTitle, registerSubmitHandler} from '../models/util.js';
import {itemTemplate} from '../templates/admin_item.html.js';
import {SideBarView} from './sidebar.js'

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
      let PriceForm = Ractive.extend({
        isolated: false,
        template: function(data) {
          if(this.get('formTemplate')) {
            // Add ractive on click event handler to the baseframe form
            return Util.getFormTemplate(this.get('formTemplate'), 'onFormSubmit(event, "edit")');
          }
          return Util.getFormTemplate(price_form, 'onFormSubmit(event, "new")');
        },
        computed: {
          formId: {
            get: function() {
              if(this.get('formTemplate')) {
                return Util.getElementId(this.get('formTemplate'));
              }
              return Util.getElementId(price_form);
            }
          }
        },
        onFormSubmit: function(event, action) {
          event.original.preventDefault();
          let formSelector = '#' + this.get('formId'),
            url = action === "edit" ? urlFor('edit', { resource: 'price', id: this.get('priceId'), root: true}) :
                  urlFor('new', { scope_ns: 'item', scope_id: item.id, resource: 'price', root: true }),
            price = action === "edit" ? 'prices.' + this.get('price') : '';

          post({
            url: url,
            data: getFormParameters(formSelector),
            formId: formSelector
          }).done((remoteData) => {
            if (action === "edit") {
              //Update the price details
              itemComponent.set(price + '.showEditForm', DEFAULT.hideForm);
              itemComponent.set(price, remoteData.result.item_collection);
            } else {
              // On creating a new price, add it to prices list
              itemComponent.viewDashboard(remoteData.result.item_collection.url_for_view);
            }
          }).fail((response) => {
            let errorMsg;
            errorMsg = formErrorHandler(response, this.get('formId'));
            itemComponent.set(price + '.errorMsg', errorMsg);
          });
        }
      });

      let itemComponent = new Ractive({
        el: '#main-content-area',
        template: itemTemplate,
        data: {
          item: item,
          prices: prices,
          itemForm: item_form,
          priceForm: {
            form: price_form,
            showAddForm: DEFAULT.hideForm,
            errorMsg: DEFAULT.empty,
          },
          discount_policies: discount_policies,
          formatToIndianRupee: function (amount) {
            return Util.formatToIndianRupee(amount);
          },
          formatDateTime: function (datetime) {
            return Util.formatDateTime(datetime);
          }
        },
        components: {PriceForm: PriceForm},
        showPriceForm: function (event, action) {
                      window.main = this;
            console.log('showPriceForm');
          if (action === "edit") {
            let price = event.keypath,
              priceId = event.context.id;
            this.set(price + '.loadingEditForm', DEFAULT.showLoader);
            fetch({
              url: urlFor('edit', { resource: 'price', id: priceId, root: true})
            }).done(({form_template}) => {
              // Set the from baseframe form html as the price's form template
              itemComponent.set(price + '.formTemplate', form_template);
              itemComponent.set(price + '.showEditForm', DEFAULT.showForm);
              itemComponent.set(price + '.loadingEditForm', DEFAULT.hideLoader);
            }).fail(() => {
              itemComponent.set(price + '.loadingEditForm', DEFAULT.hideLoader);
            })
          } else {
            this.set('priceForm.showAddForm', DEFAULT.showForm);
          }
        },
        hidePriceForm: function (event) {
          this.set('priceForm.showAddForm', DEFAULT.hideForm);
        },
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
