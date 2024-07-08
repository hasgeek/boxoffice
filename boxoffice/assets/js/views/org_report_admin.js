/* eslint-disable no-unused-vars */
import { fetch, urlFor, setPageTitle } from '../models/util';
import { OrgReportTemplate } from '../templates/admin_org_report.html';
import { SideBarView } from './sidebar';

const NProgress = require('nprogress');
const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');

export const OrgReportView = {
  render({ accountName } = {}) {
    fetch({
      url: urlFor('index', {
        resource: 'reports',
        scope_ns: 'o',
        scope_id: accountName,
        root: true,
      }),
    }).done(({ account_title: accountTitle }) => {
      // Initial render
      const currentDate = new Date();
      const currentYear = String(currentDate.getFullYear());
      // month starts from 0
      const currentMonth = String(currentDate.getMonth() + 1).padStart(2, '0');
      const prevMonth = String(((currentDate.getMonth() + 11) % 12) + 1).padStart(
        2,
        '0'
      );
      const toDate = String(currentDate.getDate()).padStart(2, '0');
      const reportComponent = new Ractive({
        el: '#main-content-area',
        template: OrgReportTemplate,
        transitions: { fly },
        data: {
          accountTitle,
          reportType: 'invoices',
          periodType: 'all',
          periodMonth: `${currentYear}-${prevMonth}`,
          currentMonth: `${currentYear}-${currentMonth}`,
          periodFrom: `${currentYear}-${currentMonth}-01`,
          periodTo: `${currentYear}-${currentMonth}-${toDate}`,
          hideForSettlementsClass() {
            return this.get('reportType') === 'settlements' ? 'hide' : '';
          },
          showForZBInvoicesClass() {
            return this.get('reportType') === 'invoices_zoho_books' ? '' : 'hide';
          },
          periodMonthlyClass() {
            if (this.get('reportType') === 'settlements') return '';
            return this.get('periodType') !== 'monthly' ? 'hide' : '';
          },
          periodCustomClass() {
            return this.get('periodType') !== 'custom'
              ? 'hide'
              : this.get('hideForSettlementsClass')();
          },
          reportsUrl() {
            const reportType = this.get('reportType');
            const url = urlFor('index', {
              resource: reportType,
              scope_ns: 'o',
              scope_id: accountName,
              ext: 'csv',
              root: true,
            });
            const params = {};
            if (reportType === 'settlements') {
              const periodMonth = this.get('periodMonth');
              if (periodMonth) [params.year, params.month] = periodMonth.split('-');
            } else {
              params.type = this.get('periodType');
              switch (params.type) {
                case 'monthly':
                  params.month = this.get('periodMonth');
                  break;
                case 'custom':
                  params.from = this.get('periodFrom');
                  params.to = this.get('periodTo');
                  break;
                default:
                  break;
              }
            }
            return `${url}?${$.param(params)}`;
          },
          reportsFilename() {
            let filename = `${accountName}_${this.get('reportType')}`;
            if (this.get('reportType') === 'settlements') {
              filename += `_${this.get('periodMonth')}`;
            } else {
              const periodType = this.get('periodType');
              switch (periodType) {
                case 'monthly':
                  filename += `_${this.get('periodMonth')}`;
                  break;
                case 'custom':
                  filename += `_${this.get('periodFrom')}_${this.get('periodTo')}`;
                  break;
                default:
                  break;
              }
            }
            filename += '.csv';
            return filename;
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
