
var NProgress = require('nprogress');
var Ractive = require('ractive');
import {fetch, urlFor, setPageTitle} from '../models/util.js';
import {ReportTemplate} from '../templates/admin_report.html.js';
import {SideBarView} from './sidebar.js';

export const ReportView = {
  render: function({ic_id}={}) {

    fetch({
      url: urlFor('index', {resource: 'reports', scope_ns: 'ic', scope_id: ic_id, root: true})
    }).done(({org_name, org_title, ic_name, ic_title}) => {
      // Initial render
      let reportComponent = new Ractive({
        el: '#main-content-area',
        template: ReportTemplate,
        data:  {
          icName: ic_name,
          icTitle: ic_title,
          reportType: "tickets",
          reportsUrl: function() {
            let reportType = this.get('reportType');
            return urlFor('index', {
              resource: reportType,
              scope_ns: 'ic',
              scope_id: ic_id,
              ext: 'csv',
              root: true
            });
          },
          reportsFilename: function() {
            return this.get('icName') + '_' + this.get('reportType') + '.csv';
          }
        }
      });

      SideBarView.render('reports', {org_name, org_title, ic_id, ic_title});
      setPageTitle("Reports", ic_title);
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
