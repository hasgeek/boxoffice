
import {setPageTitle} from '../models/util.js';
import {ReportModel} from '../models/admin_report.js';
import {ReportTemplate} from '../templates/admin_report.html.js';
import {SideBarView} from './sidebar.js';

export const ReportView = {
  render: function(config) {

    ReportModel.fetch({
      url: ReportModel.urlFor('index', {ic_id: config.id})['path']
    }).done((remoteData) => {
      // Initial render
      let reportComponent = new Ractive({
        el: '#main-content-area',
        template: ReportTemplate,
        data:  {
          title: remoteData.item_collection_title,
          reports_url: function() {
            let report_type = this.get('report_type');
            return ReportModel.urlFor(report_type, {ic_id: config.id})['path'];
          },
          reports_filename: function() {
            let filename = this.get('title').replace(/ /g, '_');
            return filename + '_' + this.get('report_type') + '.csv';
          }
        }
      });

      SideBarView.render('reports', {'org_name': remoteData.org_name, 'ic_id': config.id});
      setPageTitle(reportComponent.get('title'), "Reports");
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
