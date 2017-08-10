
import {fetch, urlFor, setPageTitle} from '../models/util.js';
import {OrgReportTemplate} from '../templates/admin_org_report.html.js';
import {SideBarView} from './sidebar.js';

export const OrgReportView = {
  render: function({org_name}={}) {
    fetch({
      url: urlFor('index', {resource: 'reports', scope_ns: 'o', scope_id: org_name, root: true})
    }).done(({name, title}) => {
      // Initial render
      let reportComponent = new Ractive({
        el: '#main-content-area',
        template: OrgReportTemplate,
        data:  {
          orgName: name,
          orgTitle: title,
          reportType: "invoices",
          reportsUrl: function() {
            let reportType = this.get('reportType');
            return urlFor('index', {
              resource: reportType,
              scope_ns: 'o',
              scope_id: name,
              ext: 'csv',
              root: true
            });
          },
          reportsFilename: function() {
            return this.get('orgName') + '_' + this.get('reportType') + '.csv';
          }
        }
      });

      SideBarView.render('org_reports', {org_name});
      setPageTitle("Organization reports", reportComponent.get('orgTitle'));
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
