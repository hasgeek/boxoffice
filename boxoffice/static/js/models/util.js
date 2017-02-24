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
  return $.ajax({
    url: config.url,
    dataType: 'json'
  });
};

export const post = function (config){
  return $.ajax({
    url: config.url,
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

export const urlFor = function(view, {org_name, ic_id}={}){
  let indexUrl = Backbone.history.root
  let baseUrl = {
    'home': {
      'path': indexUrl,
      'relative_path': '/',
      'method': 'GET'
    },
    'org': {
      'path': `${indexUrl}o/${org_name}`,
      'relative_path': `o/${org_name}`,
      'method': 'GET'
    },
    'dashboard': {
        'path': `${indexUrl}ic/${ic_id}`,
        'relative_path': `ic/${ic_id}`,
        'method': 'GET'
    },
    'orders': {
      'path': `${indexUrl}ic/${ic_id}/orders`,
      'relative_path': `ic/${ic_id}/orders`,
      'method': 'GET'
    },
    'discount-policies': {
      'path': `${indexUrl}${org_name}/discount_policy`,
      'relative_path': `${org_name}/discount_policy`,
      'method': 'GET'
    },
    'reports': {
      'path': `${indexUrl}ic/${ic_id}/reports`,
      'relative_path': `ic/${ic_id}/reports`,
      'method': 'GET'
    }
  };
  let urls = {
    'index': {
      'path': baseUrl[view]['path'],
      'relative_path':  baseUrl[view]['relative_path'],
      'method':  baseUrl[view]['method']
    },
    'new': {
      'path': `${baseUrl[view]['path']}/new`,
      'relative_path':  `${baseUrl[view]['relative_path']}/new`,
      'method':  baseUrl[view]['method']
    }
  };
  return urls;
}
