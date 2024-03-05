/* eslint-disable no-unused-vars */
import { fetch, Util, formErrorHandler } from '../models/util';

import { BaseframeForm } from './baseframe_form';

const _ = require('underscore');
const Ractive = require('ractive');
const fly = require('ractive-transitions-fly');
const NProgress = require('nprogress');

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

const FormViewSliderTemplate = `
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
  components: { BaseframeForm },
  transitions: { fly },
  data: {
    shown: false,
    title: '',
    formHTML: '',
    errors: '',
    onHide() {},
  },
  load(options) {
    fetch({ url: options.url }).then((response) => {
      this.hide();
      this.set('title', options.title);
      this.set('formHTML', response.form_template);
      if (options.onHide) {
        this.set('onHide', options.onHide);
      }
      this.show();

      const formId = Util.getElementId(response.form_template);
      const onSuccess = (responseData) => {
        this.hide();
        options.onSuccess(responseData);
      };
      const onError = (errorResponse) => {
        const errors = formErrorHandler(formId, errorResponse);
        this.set('errors', errors);
        if (_.isFunction(options.onError)) {
          options.onError(errorResponse);
        }
      };
      window.Baseframe.Forms.handleFormSubmit(
        formId,
        options.url,
        onSuccess,
        onError,
        {}
      );
      NProgress.done();
    });
  },
  show() {
    this.set('shown', true);
  },
  hide() {
    this.set('shown', false);
  },
  oncomplete() {
    /* Close the form modal when user clicks outside the modal.
      jquery-timepicker adds a div.ui-timepicker-wrapper to the body, don't close the modal
      when user selects time from the timepicker dropdown.
    */
    $(document).on('click', (event) => {
      if (
        !$(event.target).closest('#form-view .content-slider').length &&
        !$(event.target).is('#form-view .content-slider') &&
        !$(event.target).closest('.ui-timepicker-wrapper').length
      ) {
        FormView.fire('hide');
      }
    });

    // On pressing ESC, close the modal
    $(document).keydown((event) => {
      if (event.keyCode === 27) {
        event.preventDefault();
        FormView.fire('hide');
      }
    });
  },
});

FormView.on('hide', function toggleShowHide(event) {
  if (this.get('shown')) {
    this.hide();
    this.get('onHide')();
  }
});

export { FormView as default };
