export const OrgReportTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ orgTitle }}</h1>
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
              </select>
              {{#if reportType == "settlements"}}
                <p class='settlements-month-widget'>
                  <input id="month" type="month" value="{{monthYear}}">
                </p>
              {{/if}}
            </div>
            <div class="btn-wrapper"> 
              <a href="{{ reportsUrl() }}" download="{{ reportsFilename() }}" class="boxoffice-button boxoffice-button-action">Download</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
`
