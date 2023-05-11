/* eslint-disable no-unused-vars */
import { fetch, urlFor, setPageTitle } from '../models/util';
import { OrgReportTemplate } from '../templates/admin_org_report.html';
import { SideBarView } from './sidebar';

const NProgress = require('nprogress');
const Ractive = require('ractive');

export const OrgReportView = {
  render({ accountName } = {}) {
    fetch({
      url: urlFor('index', {
        resource: 'reports',
        scope_ns: 'o',
        scope_id: accountName,
        root: true,
      }),
    }).done(({ account_title: accountTitle, siteadmin }) => {
      // Initial render
      const currentDate = new Date();
      const currentYear = currentDate.getFullYear();
      // month starts from 0
      const currentMonth = currentDate.getMonth() + 1;
      const reportComponent = new Ractive({
        el: '#main-content-area',
        template: OrgReportTemplate,
        data: {
          accountTitle,
          reportType: 'invoices',
          monthYear: `${currentYear}-${currentMonth}`,
          siteadmin,
          reportsUrl() {
            const reportType = this.get('reportType');
            const url = urlFor('index', {
              resource: reportType,
              scope_ns: 'o',
              scope_id: accountName,
              ext: 'csv',
              root: true,
            });
            if (reportType === 'settlements') {
              const [year, month] = this.get('monthYear').split('-');
              return `${url}?year=${year}&month=${month}`;
            }
            return url;
          },
          reportsFilename() {
            if (this.get('reportType') === 'settlements') {
              return `${accountName}_${this.get('reportType')}_${this.get(
                'monthYear'
              )}.csv`;
            }
            return `${accountName}_${this.get('reportType')}.csv`;
          },
        },
      });

      SideBarView.render('org_reports', { accountName, accountTitle });
      setPageTitle('Organization reports', accountTitle);
      NProgress.done();

      window.addEventListener('popstate', (event) => {
        NProgress.configure({ showSpinner: false }).start();
      });
    });
  },
};

export { OrgReportView as default };
