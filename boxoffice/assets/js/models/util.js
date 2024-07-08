// A collection of utility functions

const moment = require('moment');
const Backbone = require('backbone');

export const Util = {
  formatToIndianRupee(value) {
    // Takes a floating point value and formats it to the Indian currency format
    // with the rupee sign.
    // Taken from https://github.com/hasgeek/hasjob/blob/master/hasjob/static/js/app.js
    if (!value) return value;
    let val = value.toString();
    val = val.replace(/[^0-9.]/g, ''); // Remove non-digits, assume . for decimals
    let afterPoint = '';
    if (val.indexOf('.') > 0) afterPoint = val.substring(val.indexOf('.'), val.length);
    val = Math.floor(val);
    val = val.toString();
    let lastThree = val.substring(val.length - 3);
    const otherNumbers = val.substring(0, val.length - 3);
    if (otherNumbers !== '') lastThree = `,${lastThree}`;
    const res = `₹${otherNumbers.replace(
      /\B(?=(\d{2})+(?!\d))/g,
      ','
    )}${lastThree}${afterPoint}`;
    return res;
  },
  formatDateTime(dateTimeString, formatString = '') {
    // Takes an date time string and returns a string in the specified format.
    if (formatString) {
      return moment(dateTimeString).format(formatString);
    }
    return moment(dateTimeString).toString();
  },
  getElementId(htmlString) {
    return htmlString.match(/id="(.*?)"/)[1];
  },
};

export function fetch(config) {
  return $.ajax({
    url: config.url,
    dataType: config.dataType ? config.dataType : 'json',
  });
}

export function post(config) {
  return $.ajax({
    url: config.url,
    type: 'POST',
    data: config.data,
    contentType: config.contentType
      ? config.contentType
      : 'application/x-www-form-urlencoded; charset=UTF-8',
    dataType: config.dataType ? config.dataType : 'json',
    beforeSend() {
      if (config.formId) {
        $(config.formId).find('button[type="submit"]').prop('disabled', true);
        $(config.formId).find('.loading').removeClass('hidden');
      }
    },
  });
}

export function xhrRetry(
  ajaxLoad,
  response,
  serverErrorCallback,
  networkErrorCallback
) {
  if (response.readyState === 4) {
    // Server error
    serverErrorCallback();
  } else if (response.readyState === 0) {
    if (ajaxLoad.retries < 0) {
      // Network error
      networkErrorCallback();
    } else {
      setTimeout(() => {
        $.ajax(ajaxLoad);
      }, ajaxLoad.retryInterval);
    }
  }
}

export function getFormParameters(form) {
  return $.param($(form).serializeArray());
}

export function getFormJSObject(form) {
  const formElements = $(form).serializeArray();
  const formDetails = {};
  $.each(formElements, function updateFormDetails() {
    if (formDetails[this.name] !== undefined) {
      if (!formDetails[this.name].push) {
        formDetails[this.name] = [formDetails[this.name]];
      }
      formDetails[this.name].push(this.value || '');
    } else {
      formDetails[this.name] = this.value || '';
    }
  });
  return formDetails;
}

export function getCsrfToken() {
  return document.head.querySelector('[name=csrf-token]').content;
}

export function formErrorHandler(formId, errorResponse) {
  let errorMsg = '';
  // xhr readyState '4' indicates server has received the request & response is ready
  if (errorResponse.readyState === 4) {
    if (errorResponse.status === 500) {
      errorMsg = 'Internal Server Error';
    } else {
      window.Baseframe.Forms.showValidationErrors(
        formId,
        errorResponse.responseJSON.errors
      );
      errorMsg = 'Error';
    }
  } else {
    errorMsg = 'Unable to connect. Please try again.';
  }
  $(`#${formId}`).find('button[type="submit"]').prop('disabled', false);
  $(`#${formId}`).find('.loading').addClass('hidden');
  return errorMsg;
}

export function scrollToElement(element, speed = 500) {
  $('html,body').animate(
    {
      scrollTop: $(element).offset().top,
    },
    speed
  );
}

export function updateBrowserHistory(newUrl) {
  window.history.replaceState({ reloadOnPop: true }, '', window.location.href);
  window.history.pushState({ reloadOnPop: true }, '', newUrl);
}

export function urlFor(action, params = {}) {
  /*
  Returns a URL for a given resource and action.

  `action` is a required parameter and MUST be one of 'index', 'view',
  'new', 'edit' or 'search'.

  The URLs provided follow the following pattern for a particular resource:
  - 'index' -> /
  - 'view' -> /<id>
  - 'new' -> /new
  - 'edit' -> /edit
  - 'search' -> /?search=search

  :params is an object and can contain
  - scope_ns: scope namespace
  - scope_id: scope object primary key
  - resource: resource name
  - id      : resource id
  - search  : search term
  - ext     : file extension
  - page    : page number of the payload, if paginated
  - size    : size of the payload, if paginated
  - root    : Boolean, in case the URL needs to be prefixed with root namespace eg: /admin
  */
  const rootURL = Backbone.history.root;
  let scope = '';
  let ext = '';
  let resource = '';
  let url;

  if (params.scope_ns && params.scope_id) {
    scope = `${params.scope_ns}/${params.scope_id}/`;
  }

  if (params.resource) {
    resource = `${params.resource}`;
  }

  if (params.ext) {
    ext = `.${params.ext}`;
  }

  switch (action) {
    case 'index':
      if (params.page) {
        url = `${scope}${resource}${ext}?page=${params.page}&size=${params.size}`;
      } else if (params.size) {
        url = `${scope}${resource}${ext}?size=${params.size}`;
      } else {
        url = `${scope}${resource}${ext}`;
      }
      break;
    case 'view':
      url = scope
        ? `${scope}${resource}/${params.id}${ext}`
        : `${resource}/${params.id}${ext}`;
      break;
    case 'new':
      url = `${scope}${resource}/new`;
      break;
    case 'edit':
      url = `${scope}${resource}/${params.id}/edit`;
      break;
    case 'search':
      url = params.page
        ? `${scope}${resource}?search=${params.search}&page=${params.page}&size=${params.size}`
        : `${scope}${resource}?search=${params.search}`;
      break;
    default:
      url = params.id
        ? `${scope}${resource}/${params.id}/${action}`
        : `${scope}${resource}/${action}`;
  }

  if (params.root) {
    url = rootURL + url;
  }

  return url;
}

export function setPageTitle(...subTitles) {
  /* Takes an array of titles and returns a concatenated string separated by " — ".
  Eg:- "Orders — JSFoo 2016 — Boxoffice" */
  subTitles.push(window.boxofficeAdmin.siteTitle);
  $('title').html(subTitles.join(' — '));
}
