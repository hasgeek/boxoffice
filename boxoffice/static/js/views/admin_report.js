
import {ReportModel} from '../models/admin_report.js';
import {ReportTemplate} from '../templates/admin_report.html.js';
import {SideBarView} from './sidebar.js';

export const ReportView = {
  render: function(config) {

    ReportModel.fetch({
      url: ReportModel.urlFor('index', {icId: config.id})['path']
    }).done((remoteData) => {
      // Initial render
      let reportComponent = new Ractive({
        el: '#main-content-area',
        template: ReportTemplate,
        data:  {
          title: remoteData.item_collection_title,
          reportsUrl: function() {
            let reportType = this.get('reportType');
            return ReportModel.urlFor(reportType, {icId: config.id})['path'];
          },
          reportsFilename: function() {
            let filename = this.get('title').replace(/ /g, '_');
            return filename + '_' + this.get('reportType') + '.csv';
          }
        }
      });

      SideBarView.render('reports', {'orgName': remoteData.org_name, 'icId': config.id});

      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false}).start();
      });
    });
  }
};
