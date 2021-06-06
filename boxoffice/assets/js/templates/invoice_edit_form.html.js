export const InvoiceEditFormTemplate = `
  {{#each invoices}}
    <div class="ticket col-xs-12 {{#if invoices.length > 1}}col-sm-6{{else}}col-sm-8 col-sm-offset-2 col-md-6 col-md-offset-3{{/if}}">
      <div class="content-box clearfix" intro='fly:{"x":20,"y":"0"}'>
        {{#if !hideForm}}
          <h4 class="text-center attendee-form-title">If you need a GST invoice, please fill in the details below.</h4>
            <form class="attendee-form clearfix" role="form" name="invoice-details-form-{{ id }}" id="invoice-{{ id }}">
              <div class="group">
                <input class="group-input {{#buyer_taxid}}filled{{/}}" type="text" name="buyer_taxid" value="{{ buyer_taxid }}">
                <span class="bar"></span>
                <label class="group-label">GSTIN</label>
                {{#errormsg.buyer_taxid}}<p class="form-error-msg">{{ errormsg.buyer_taxid }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#invoicee_name}}filled{{/}}" type="text" name="invoicee_name" value="{{ invoicee_name }}">
                <span class="bar"></span>
                <label class="group-label">Name</label>
                {{#errormsg.invoicee_name}}<p class="form-error-msg">{{ errormsg.invoicee_name }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#invoicee_company}}filled{{/}}" type="text" name="invoicee_company" value="{{ invoicee_company }}">
                <span class="bar"></span>
                <label class="group-label">Company</label>
                {{#errormsg.invoicee_company}}<p class="form-error-msg">{{ errormsg.invoicee_company }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#invoicee_email}}filled{{/}}" type="text" name="invoicee_email" value="{{ invoicee_email }}">
                <span class="bar"></span>
                <label class="group-label">Email</label>
                {{#errormsg.invoicee_email}}<p class="form-error-msg">{{ errormsg.invoicee_email }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#street_address_1}}filled{{/}}" type="text" name="street_address_1" value="{{ street_address_1 }}">
                <label class="group-label">Street address 1</label>
                {{#errormsg.street_address_1}}<p class="form-error-msg">{{ errormsg.street_address_1 }}</p>{{/}}
              </div>
              <div class="group">
                <input class="group-input {{#street_address_2}}filled{{/}}" type="text" name="street_address_2" value="{{ street_address_2 }}">
                <label class="group-label">Street address 2</label>
                {{#errormsg.street_address_2}}<p class="form-error-msg">{{ errormsg.street_address_2 }}</p>{{/}}
              </div>
              <div class="group-select inline-group left-group">
                <select name="country_code" value="{{country_code}}">
                  {{#utils.countries}} {{# { country: . } }}
                    <option value="{{ country.code }}">{{ country.name }}</option>
                  {{/}}{{/utils.countries}}
                </select>
                {{#errormsg.country_code}}<p class="form-error-msg">{{ errormsg.country_code }}</p>{{/}}
              </div>
              {{#if country_code == "IN"}}
                <div class="group-select inline-group right-group">
                  <select name="state_code" value="{{ state_code }}">
                    <option value="">Select a state</option>
                    {{#utils.states}} {{# { currentState: . } }}
                      <option value="{{ currentState.code }}">{{ currentState.name }}</option>
                    {{/}}{{/utils.states}}
                  </select>
                  {{#errormsg.state_code}}<p class="form-error-msg">{{ errormsg.state_code }}</p>{{/}}
                  <input class="hidden" type="radio" name="{{ state }}" value="" checked>
                </div>
              {{else}}
                <div class="group inline-group right-group">
                  <input class="group-input right-group {{#state}}filled{{/}}" type="text" name="state" value="{{ state }}">
                  <span class="bar"></span>
                  <label class="group-label">State</label>
                  {{#errormsg.state}}<p class="form-error-msg">{{ errormsg.state }}</p>{{/}}
                  <input class="hidden" type="radio" name="{{ state_code }}" value="" checked>
                </div>
              {{/if}}
              <div class="group inline-group left-group">
                <input class="group-input {{#city}}filled{{/}}" type="text" name="city" value="{{ city }}">
                <span class="bar"></span>
                <label class="group-label">City</label>
                {{#errormsg.city}}<p class="form-error-msg">{{ errormsg.city }}</p>{{/}}
              </div>
              <div class="group inline-group right-group">
                <input class="group-input right-group {{#postcode}}filled{{/}}" type="text" name="postcode" value="{{ postcode }}">
                <span class="bar"></span>
                <label class="group-label">Pincode</label>
                {{#errormsg.postcode}}<p class="form-error-msg">{{ errormsg.postcode }}</p>{{/}}
              </div>
              <div class="assign-btn-wrapper">
                <button type="submit" class="boxoffice-button boxoffice-button-action" on-click="submitInvoiceDetails(event, event.keypath, id)" {{#submittingInvoiceDetails}}disabled{{/}}>
                  Update {{#submittingInvoiceDetails}}<i class="fa fa-spinner fa-spin" intro='fly:{"x":0,"y":"0"}'>{{/}}
                </button>
              </div>
            </form>
            {{#errorMsg}}
              <div class="error-msg">{{{ errorMsg }}}</div>
            {{/}}
        {{else}}
          <p class="confirmation-msg">Thank you for submitting the details, we will mail you the invoice shortly.</p>
          <div class="assign-btn-wrapper">
            <button type="submit" class="boxoffice-button boxoffice-button-info" on-click="showInvoiceForm(event, event.keypath)">Edit invoice details</button>
          </div>
        {{/if}}
      </div>
    </div>
  {{/each}}
`;
