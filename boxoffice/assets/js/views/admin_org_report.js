var NProgress = require('nprogress');
var Ractive = require('ractive');
import { fetch, urlFor, setPageTitle } from '../models/util.js';
import { OrgReportTemplate } from '../templates/admin_org_report.html.js';
import { SideBarView } from './sidebar.js';

export const OrgReportView = {
  render: function ({ org_name } = {}) {
    fetch({
      url: urlFor('index', {
        resource: 'reports',
        scope_ns: 'o',
        scope_id: org_name,
        root: true,
      }),
    }).done(({ org_title, siteadmin }) => {
      // Initial render
      let currentDate = new Date();
      let currentYear = currentDate.getFullYear();
      // month starts from 0
      let currentMonth = currentDate.getMonth() + 1;
      let reportComponent = new Ractive({
        el: '#main-content-area',
        template: OrgReportTemplate,
        data: {
          orgTitle: org_title,
          reportType: 'invoices',
          monthYear: `${currentYear}-${currentMonth}`,
          siteadmin: siteadmin,
          reportsUrl: function () {
            let reportType = this.get('reportType');
            let url = urlFor('index', {
              resource: reportType,
              scope_ns: 'o',
              scope_id: org_name,
              ext: 'csv',
              root: true,
            });
            if (reportType === 'settlements') {
              let year, month;
              [year, month] = this.get('monthYear').split('-');
              return `${url}?year=${year}&month=${month}`;
            } else {
              return url;
            }
          },
          reportsFilename: function () {
            if (this.get('reportType') === 'settlements') {
              return `${org_name}_${this.get('reportType')}_${this.get(
                'monthYear'
              )}.csv`;
            } else {
              return `${org_name}_${this.get('reportType')}.csv`;
            }
          },
        },
      });

      SideBarView.render('org_reports', { org_name, org_title });
      setPageTitle('Organization reports', org_title);
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false }).start();
      });
    });
  },
};
