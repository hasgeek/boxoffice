import { fetch, urlFor, setPageTitle } from '../models/util';
import { ReportTemplate } from '../templates/admin_report.html';
import { SideBarView } from './sidebar';

const NProgress = require('nprogress');
const Ractive = require('ractive');

export const ReportView = {
  render({ menuId } = {}) {
    fetch({
      url: urlFor('index', {
        resource: 'reports',
        scope_ns: 'menu',
        scope_id: menuId,
        root: true,
      }),
    }).done(
      ({
        account_name: accountName,
        account_title: accountTitle,
        menu_name: menuName,
        menu_title: menuTitle,
      }) => {
        // Initial render
        const reportComponent = new Ractive({
          el: '#main-content-area',
          template: ReportTemplate,
          data: {
            menuName,
            menuTitle,
            reportType: 'tickets',
            reportsUrl() {
              const reportType = this.get('reportType');
              return urlFor('index', {
                resource: reportType,
                scope_ns: 'menu',
                scope_id: menuId,
                ext: 'csv',
                root: true,
              });
            },
            reportsFilename() {
              return `${this.get('menuName')}_${this.get('reportType')}.csv`;
            },
          },
        });

        SideBarView.render('reports', {
          accountName,
          accountTitle,
          menuId,
          menuTitle,
        });
        setPageTitle('Reports', menuTitle);
        NProgress.done();

        window.addEventListener('popstate', (event) => {
          NProgress.configure({ showSpinner: false }).start();
        });
      }
    );
  },
};

export { ReportView as default };
