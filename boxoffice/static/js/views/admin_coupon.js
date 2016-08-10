
import {DiscountCouponModel} from '../models/admin_coupon.js';
import {DiscountCouponTemplate} from '../templates/admin_coupon.html.js';
import {SideBarView} from './sidebar.js';

export const DiscountCouponView = {
  render: function(config) {

    DiscountCouponModel.fetch({
      url: DiscountCouponModel.urlFor('index', {org_name: config.org_name})['path']
    }).done((remoteData) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: DiscountCouponTemplate,
        data:  {
          org: remoteData.org_name,
          title: remoteData.title,
          coupons: remoteData.coupons
        }
      });

      SideBarView.render('coupons', {'org_name': remoteData.org_name});

      NProgress.done();

      $('#coupons-table').footable({
        breakpoints: {
          phone: 600,
          tablet: 768,
          desktop: 1200,
          largescreen: 1900
        }
      });

      main_ractive.on('showCouponUsage', function(event){
        //Show individual coupon usage details
        main_ractive.set(event.keypath + '.loading', true);
        let coupon_id = event.context.id;
        DiscountCouponModel.fetch({
          url: DiscountCouponModel.urlFor('view', {org_name: main_ractive.get('org'), coupon_id:coupon_id})['path']
        }).done((remoteData) => {
          main_ractive.set(event.keypath + '.line_items', remoteData.line_items);
          main_ractive.set(event.keypath + '.loading', false);
          main_ractive.set(event.keypath + '.show_coupon_usage', true);
          $("#" + coupon_id).footable();
        });
      });

      main_ractive.on('hideCouponUsage', function(event){
        main_ractive.set(event.keypath + '.show_coupon_usage', false);
      });

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
