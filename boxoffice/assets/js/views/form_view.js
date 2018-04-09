
var _ = require("underscore");
var Ractive = require('ractive');
var NProgress = require('nprogress');
import {fetch, Util, formErrorHandler} from '../models/util.js';
import {BaseframeForm} from './baseframe_form.js';

/*
** `FormView` provides an interface to show a form to create or edit a resource.
** 
** `FormView` accepts the following parameters:
** `url`: The `url` from which a resource's form needs to be loaded
** `title`: The title for the view
** `onHide`: A handler that is called when the form view is hidden
** `onSuccess`: A handler that is called when a form submit is successful. Called with `responseData`
** `onError`: A handler that is invoked when a form submit fails. Called with `response`.
**
** `FormView` provides the following methods:
** `show`: shows the detail view as a slider
** `hide`: hides the detail view
** `load`: loads a specific resource and handles a form if necessary.

** Register proxy events on `FormView` if necessary
*/

let FormViewSliderTemplate = `
  {{#if shown}}
    <div class="modal-background"></div>
    <div class="content-slider" intro-outro='fly:{x:0,y:200,duration:200}'>
      <p class="content-slider-title clearfix">
        <span class="title">{{{title}}}</span>
        <button class="hide-button" on-click="hide"><i class="fa fa-close"></i></button>
      </p>
      <div class="content-slider-wrapper">
        <BaseframeForm html="{{ formHTML }}"></BaseframeForm>
        <p class="error-msg">{{{errors}}}</p>
      </div>
    </div>
  {{/if}}
`;

export const FormView = new Ractive({
  el: '#form-view',
  template: FormViewSliderTemplate,
  components: {BaseframeForm: BaseframeForm},
  data: {
    shown: false,
    title: '',
    formHTML: '',
    errors: '',
    onHide: function(){}
  },
  load: function(options){
    fetch({url: options.url}).then((response) => {
      this.hide();
      this.set('title', options.title);
      this.set('formHTML', response.form_template);
      if (options.onHide){
        this.set('onHide', options.onHide);
      }
      this.show();

      var formId = Util.getElementId(response.form_template);
      var onSuccess = (responseData) => {
        this.hide();
        options.onSuccess(responseData);
      }
      var onError = (response) => {
        var errors = formErrorHandler(formId, response);
        this.set('errors', errors);
        if (_.isFunction(options.onError)) {
          options.onError(response);
        }
      }
      Baseframe.Forms.handleFormSubmit(formId, options.url, onSuccess, onError, {});
      NProgress.done();
    });
  },
  show: function(){
    this.set('shown', true);
  },
  hide: function(){
    this.set('shown', false);
  },
  oncomplete: function () {
    //Close the form modal when user clicks outside the modal
    $(document).on("click", function(event) {
      if (!$(event.target).closest('#form-view .content-slider').length && !$(event.target).is('#form-view .content-slider')) {
        FormView.fire('hide');
      }
    });

    //On pressing ESC, close the modal
    $(document).keydown(function(event) {
      if (event.keyCode === 27) {
        event.preventDefault();
        FormView.fire('hide');
      }
    });
  }
});

FormView.on('hide', function(event) {
  if (this.get('shown')) {
    this.hide();
    this.get('onHide')();
  }
});
