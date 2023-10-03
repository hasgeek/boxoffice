export const OrgReportTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ accountTitle }}</h1>
    <div class="box col-sm-6 col-sm-offset-3 col-xs-12">
      <div class="heading">
        <p class="heading-title">Download reports</p>
      </div>
      <div class="content">
        <div class="content-box">
          <form role="form" id="report-form">
            <div class="group-select">
              <p class="field-title filled">Report type</p>
              <select name="report-type" value="{{ reportType }}">
                <option value="invoices" selected="selected">Invoices</option>
                <option value="settlements">Settlements</option>
                <option value="invoices_zoho_books">Zoho Books Invoices</option>
              </select>
            </div>
            <div class="group-select {{hideForSettlementsClass()}}">
              <p class="field-title filled">Filter by period</p>
              <select name="period-type" value="{{ periodType }}">
                <option value="all" selected="selected">All</option>
                <option value="monthly">Monthly</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div class="report-period">
              <p class="field-title filled {{periodMonthlyClass()}}">Month</p>
              <p class="{{periodMonthlyClass()}}">
                <input id="month" type="month" value="{{periodMonth}}" max="{{currentMonth}}">
              </p>
              <p class="field-title filled {{periodCustomClass()}}">From</p>
              <p class="{{periodCustomClass()}}">
                <input id="period-from" type="date" name="from" value="{{periodFrom}}" max="{{periodTo}}">
              </p>
              <p class="field-title filled {{periodCustomClass()}}">To</p>
              <p class="{{periodCustomClass()}}">
                <input id="period-to" type="date" name="to" value="{{periodTo}}" max="{{periodTo}}">
              </p>
            </div>
            <div class="btn-wrapper">
              <a href="{{ reportsUrl() }}" download="{{ reportsFilename() }}" class="boxoffice-button boxoffice-button-action">Download</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
`;

export { OrgReportTemplate as default };
