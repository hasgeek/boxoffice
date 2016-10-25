
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
              <select name="type" value="{{report_type}}">
                <option value="tickets">Tickets</option>
                <option value="attendees">Attendees</option>
              </select>
            </div>
            <div class="btn-wrapper"> 
              <a href="{{reports_url()}}" download="{{reports_filename()}}" class="boxoffice-button boxoffice-button-action">Download</a>
            </div>
            <p class="error-msg">{{download_report_error}}</p>
          </form>
        </div>
      </div>
    </div>
  </div>
`
