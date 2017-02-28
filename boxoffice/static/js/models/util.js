// A collection of utility functions

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
  }
};

export const fetch = function (config){
  let url = config.url;
  if (!config.absolute) {
    url = Backbone.history.root + config.url;
  }
  return $.ajax({
    url: url,
    dataType: 'json'
  });
};

export const post = function (config){
  let url = config.url;
  if (config.absolute) {
    url = Backbone.history.root + config.url;
  }
  return $.ajax({
    url: url,
    type: 'POST',
    data: config.data,
    contentType : config.contentType ? config.contentType : 'application/x-www-form-urlencoded; charset=UTF-8',
    dataType: 'json',
  });
};

export const scrollToElement = function (element, speed=500) {
  $('html,body').animate({
    scrollTop: $(element).offset().top
  }, speed);
};

export const getFormParameters = function (form) {
  var form_elements = $(form).serializeArray();
  return $.param(form_elements);
};

export const getCsrfToken = function () {
  return document.head.querySelector("[name=csrf-token]").content;
};

export const updateBrowserHistory = function (currentUrl, newUrl) {
  window.history.replaceState({reloadOnPop: true}, '', currentUrl);
  window.history.pushState({reloadOnPop: true}, '', newUrl);
}

export const urlFor = function(view, params={}){
  /*
  Returns a URL for a given resource and action.
  
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
  - root    : if URL should be prefixed with root namespace eg: /admin
  */
  let rootURL = Backbone.history.root;
  var indexPath = rootURL;
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
    ext = `.${params.ext}/`;
  }

  if (view === 'index' || view === 'search') {
    indexPath = `${scope}${resource}`;
  }

  let urlMap = {
    'index': `${indexPath}${ext}`,
    'view': `${scope}${resource}/${params.id}${ext}`,
    'new': `${scope}${resource}/new`,
    'edit': `${scope}${resource}/${params.id}/edit`,
    'search': params.page ? `${indexPath}?search=${params.search}&page=${params.page}` : `${indexPath}?search=${params.search}`
  };

  url = urlMap[view];
  if (params.root) {
    url = rootURL + url;
  }
  return url;
}
