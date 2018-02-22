
var Ractive = require('ractive');
import {fetch, Util, formErrorHandler} from '../models/util.js';
import {navigateBack} from './main_admin.js';

/*
** `DetailView` provides an interface to show a specific resource's details
** or to show a form to create or edit a resource.
** 
** `DetailView` accepts the following parameters:
** `url`: The `url` from which a resource's content for form needs to be loaded
** `title`: The title for the view
** `handleForm`: Set this to `true` if a server generated form is expected to be rendered and handled
** `onSuccess`: A handler that is called when a form submit is successful. Called with `responseData`
** `onError`: A handler that is invoked when a form submit fails. Called with `response`.
** `template`: Use this to display a custom template. If the template requires custom attributes, set it using
** the `attributes` hash. Eg: `DetailView.set('attributes.custom_title', 'Custom title');`
**
** `DetailView` provides the following methods:
** `show`: shows the detail view as a slider
** `hide`: hides the detail view
** `load`: loads a specific resource and handles a form if necessary.

** Register proxy events on `DetailView` if necessary
*/


let DetailViewSliderTemplate = `
  {{#if shown}}
    <div class="content-slider align-down" intro-outro='fly:{x:200,y:0,duration:200}'>
      <button class="close-button" on-click="hide"><i class="fa fa-close"></i></button>
      <p class="content-slider-title">{{{title}}}</p>
      <div class="content-slider-wrapper">
        {{#if handleForm}}
          {{{ formHTML }}}
          <p class="error-msg">{{{errors}}}</p>
        {{else}}
          {{{template}}}
        {{/if}}
      </div>
    </div>
  {{/if}}
`;

export const DetailView = new Ractive({
  el: '#detail-view',
  template: DetailViewSliderTemplate,
  data: {
    shown: false,
    title: '',
    formHTML: '',
    errors: '',
    handleForm: false,
    template: '',
    // Use this to set custom attributes in the template
    attributes: {}
  },
  load: function(options){
    fetch({url: options.url}).then((response) => {
      this.hide();
      this.set('title', options.title);
      this.show();
      if (options.handleForm) {
        this.handleForm(response, options);
      } else {
        this.handleTemplate(response, options);
      }
    });
  },
  show: function(){
    this.set('shown', true);
  },
  hide: function(){
    this.set('shown', false);
  },
  handleForm: function(response, options){
    this.set('handleTemplate', false);
    this.set('handleForm', true);
    this.set('formHTML', response.form_template);
    var formId = Util.getElementId(response.form_template);
    var onSuccess = (responseData) => {
      this.hide();
      options.onSuccess(responseData);
    }
    var onError = (response) => {
      var errors = formErrorHandler(response, formId);
      this.set('errors', errors);
      if (typeof options.onError === 'object'){
        options.onError(response);
      }
    }
    Baseframe.Forms.handleFormSubmit(formId, options.url, onSuccess, onError, {});
  },
  handleTemplate: function(response, options){
    this.set('handleForm', false);
    this.set('handleTemplate', true);
    this.set('template', options.template);
  }
});

DetailView.on('hide', function(event){
  this.hide();
  navigateBack();
});
