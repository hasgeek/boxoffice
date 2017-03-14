
import {fetch, urlFor} from '../models/util.js';
import {ReportTemplate} from '../templates/admin_report.html.js';
import {SideBarView} from './sidebar.js';

export const ReportView = {
  render: function({ic_id}={}) {
    fetch({
      url: urlFor('index', {resource: 'reports', scope_ns: 'ic', scope_id: ic_id, root: true})
    }).done(({org_name, title}) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: ReportTemplate,
        data:  {
          title: title,
          reports_url: function() {
            let report_type = this.get('report_type');
            return urlFor('index', {
              resource: report_type,
              scope_ns: 'ic',
              scope_id: ic_id,
              ext: 'csv',
              root: true
            });
          },
          reports_filename: function() {
            let filename = this.get('title').replace(/ /g, '_');
            return filename + '_' + this.get('report_type') + '.csv';
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
