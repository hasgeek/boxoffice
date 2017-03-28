// A collection of utility functions

export const Util = {
  formatToIndianRupee: function(value) {
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
}

export const fetch = function(config){
  return $.ajax({
    url: config.url,
    dataType: 'json'
  });
}

export const post = function(config){
  return $.ajax({
    url: config.url,
    type: 'POST',
    contentType : config.json ? 'application/json' : 'application/x-www-form-urlencoded; charset=UTF-8',
    data: config.data,
    dataType: 'json'
  });
}

export const scrollToElement = function(element, speed=500) {
  $('html,body').animate({
    scrollTop: $(element).offset().top
  }, speed);
}

export const getFormParameters = function (form) {
  var form_elements = $(form).serializeArray();
  return $.param(form_elements);
};

export const getCsrfToken = function () {
  return document.head.querySelector("[name=csrf-token]").content;
};

export const getErrorMsg = function (response) {
	var errorMsg;
  if (response.readyState === 4) {
		if (response.status === 500) {
		  errorMsg = "Server Error";
		}
		else {
		  errorMsg = JSON.parse(response.responseText).error_description;
		}
	}
	else {
		errorMsg = "Unable to connect. Please try again later.";
	}
	return errorMsg;
};
