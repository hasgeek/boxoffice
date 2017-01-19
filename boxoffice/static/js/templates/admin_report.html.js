
export const ReportTemplate = `
  <div class="content-wrapper">
    <h1 class="header">{{ title }}</h1>
    <div class="box col-sm-6 col-sm-offset-3 col-xs-12">
      <div class="heading">
        <p class="heading-title">Download reports</p>
      </div>
      <div class="content">
        <div class="content-box">
          <form role="form" id="report-form"> 
            <div class="group-select">
              <p class="field-title filled">Report type</p>
              <select name="type" value="{{ reportType }}">
                <option value="tickets">Tickets</option>
              </select>
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
