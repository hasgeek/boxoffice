
import {ReportModel} from '../models/admin_report.js';
import {ReportTemplate} from '../templates/admin_report.html.js';
import {SideBarView} from './sidebar.js';

export const ReportView = {
  render: function(view, {ic_id}={}) {

    ReportModel.fetch({
      url: ReportModel.urlFor(view, 'index', {ic_id})['path']
    }).done(({org_name, title}) => {
      // Initial render
      let main_ractive = new Ractive({
        el: '#main-content-area',
        template: ReportTemplate,
        data:  {
          title: title,
          reports_url: function() {
            let report_type = this.get('report_type');
            return ReportModel.urlFor(view, report_type, {ic_id})['path'];
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
