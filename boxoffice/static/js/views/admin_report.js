
import {fetch, urlFor} from '../models/util.js';
import {ReportTemplate} from '../templates/admin_report.html.js';
import {SideBarView} from './sidebar.js';

export const ReportView = {
  render: function({ic_id}={}) {
    fetch({
      url: urlFor('index', {resource: 'reports', scope_ns: 'ic', scope_id: ic_id, root: true})
    }).done(({org_name, title, name}) => {
      // Initial render
      let reportsComponent = new Ractive({
        el: '#main-content-area',
        template: ReportTemplate,
        data:  {
          title: title,
          name: name,
          // default selected value of report-type
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
            return this.get('name') + '_' + this.get('reportType') + '.csv';
          }
        }
      });
      
      SideBarView.render('reports', {org_name, ic_id});

      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
