// A collection of utility functions
var moment = require("moment");

export const Util = {
  formatToIndianRupee: function (value) {
    // Takes a floating point value and formats it to the Indian currency format
    // with the rupee sign.
    // Taken from https://github.com/hasgeek/hasjob/blob/master/hasjob/static/js/app.js
    value = value.toString();
    value = value.replace(/[^0-9.]/g, '');  // Remove non-digits, assume . for decimals
    var afterPoint = '';
    if (value.indexOf('.') > 0)
      afterPoint = value.substring(value.indexOf('.'), value.length);
    value = Math.floor(value);
    value = value.toString();
    var lastThree = value.substring(value.length - 3);
    var otherNumbers = value.substring(0, value.length - 3);
    if (otherNumbers !== '')
        lastThree = ',' + lastThree;
    var res = '₹' + otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree + afterPoint;
    return res;
  },
  formatDateTime: function (dateTimeString, formatString="") {
    // Takes an date time string and returns a string in the specified format.
    if (formatString) {
      return moment(dateTimeString).format(formatString);
    }
    else {
      return moment(dateTimeString).toString();
    }
  },
  getElementId: function(htmlString) {
    return htmlString.match(/id="(.*?)"/)[1];
  }
};

export const fetch = function (config) {
  return $.ajax({
    url: config.url,
    dataType: config.dataType ? config.dataType : 'json'
  });
};

export const post = function (config) {
  return $.ajax({
    url: config.url,
    type: 'POST',
    data: config.data,
    contentType : config.contentType ? config.contentType : 'application/x-www-form-urlencoded; charset=UTF-8',
    dataType: config.dataType ? config.dataType : 'json',
    beforeSend: function() {
      if (config.formId) {
        $(config.formId).find('button[type="submit"]').prop('disabled', true);
        $(config.formId).find(".loading").removeClass('hidden');
      }
    }
  });
};

export const xhrRetry = function(ajaxLoad, response, serverErrorCallback, networkErrorCallback) {
  if (response.readyState === 4) {
    //Server error
    serverErrorCallback();
  }
  else if (response.readyState === 0) {
    if (ajaxLoad.retries < 0) {
      //Network error
      networkErrorCallback();
    }
    else {
      setTimeout(function() {
        $.ajax(ajaxLoad);
      }, ajaxLoad.retryInterval);
    }
  }
};

export const getFormParameters = function (form) {
  return $.param($(form).serializeArray());
};

export const getFormJSObject = function (form) {
  var formElements = $(form).serializeArray();
  var formDetails ={};
  $.each(formElements, function () {
    if (formDetails[this.name] !== undefined) {
      if (!formDetails[this.name].push) {
        formDetails[this.name] = [formDetails[this.name]];
      }
      formDetails[this.name].push(this.value || '');
    }
    else {
      formDetails[this.name] = this.value || '';
    }
  });
  return formDetails;
}

export const getCsrfToken = function () {
  return document.head.querySelector("[name=csrf-token]").content;
};

export const formErrorHandler = function(errorResponse, formId) {
  let errorMsg = "";
  // xhr readyState '4' indicates server has received the request & response is ready
  if (errorResponse.readyState === 4) {
    if (errorResponse.status === 500) {
      errorMsg = "Internal Server Error";
    } else {
      window.Baseframe.Forms.showValidationErrors(formId, errorResponse.responseJSON.errors);
      errorMsg = "Error";
    }
  } else {
    errorMsg = "Unable to connect. Please try again.";
  }
  $("#" + formId).find('button[type="submit"]').prop('disabled', false);
  $("#" + formId).find(".loading").addClass('hidden');
  return errorMsg;
};

export const scrollToElement = function (element, speed=500) {
  $('html,body').animate({
    scrollTop: $(element).offset().top
  }, speed);
};

export const updateBrowserHistory = function (newUrl) {
  window.history.replaceState({reloadOnPop: true}, '', window.location.href);
  window.history.pushState({reloadOnPop: true}, '', newUrl);
}

export const urlFor = function(action, params={}) {
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
  let rootURL = Backbone.history.root;
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
      url = params.page ? `${scope}${resource}${ext}?page=${params.page}&size=${params.size}` : params.size ? `${scope}${resource}${ext}?size=${params.size}` : `${scope}${resource}${ext}`;
      break;
    case 'view':
      url = scope ? `${scope}${resource}/${params.id}${ext}` : `${resource}/${params.id}${ext}`;
      break;
    case 'new':
      url = `${scope}${resource}/new`;
      break;
    case 'edit':
      url = `${resource}/${params.id}/edit`;
      break;
    case 'search':
      url = params.page ? `${scope}${resource}?search=${params.search}&page=${params.page}&size=${params.size}` : `${scope}${resource}?search=${params.search}`;
      break;
  }

  if (params.root) {
    url = rootURL + url;
  }

  return url;
}

export const setPageTitle = function (...subTitles) {
  /* Takes an array of titles and returns a concatenated string separated by " — ".
  Eg:- "Orders — JSFoo 2016 — Boxoffice" */
  subTitles.push(window.boxofficeAdmin.siteTitle);
  $('title').html(subTitles.join(" — "));
}
