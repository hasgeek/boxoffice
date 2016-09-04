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
    data: config.data,
    contentType : config.contentType,
    dataType: 'json'
  });
}

export const convertFormToJSON = function(form, multiple_option_fields){
  let form_elements = $(form).serializeArray();
  let details = {};
  for (var form_index=0; form_index < form_elements.length; form_index++) {
    if (form_elements[form_index].value) {
      if(multiple_option_fields.indexOf(form_elements[form_index].name) !== -1) {
        if(form_elements[form_index].name in details) {
          details[form_elements[form_index].name].push(form_elements[form_index].value)
        }
        else {
          details[form_elements[form_index].name] = [].concat(form_elements[form_index].value);
        }
      }
      else {
        details[form_elements[form_index].name] = form_elements[form_index].value;
      }
    }
  }
  return JSON.stringify(details);
}
