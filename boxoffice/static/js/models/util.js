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
    contentType : config.contentType ? config.contentType : 'application/x-www-form-urlencoded; charset=UTF-8',
    dataType: 'json',
  });
}

export const getFormParameters = function(form, multiple_option_fields) {
  var form_elements = $(form).serializeArray();
  for (var field=0; field < multiple_option_fields.length; field++) {
    for (var form_index=0; form_index < form_elements.length; form_index++) {
      if (form_elements[form_index].value && multiple_option_fields[field] == form_elements[form_index].name) {
        let values = form_elements[form_index].value.split(',');
        for (var index=0; index < values.length; index++) {
          if(index === 0){
            form_elements[form_index].value = values[0];
          }
          else {
            form_elements.push({'name': multiple_option_fields[field], 'value': values[index]})
          }
        }
        break;
      }
    }
  }
  return $.param(form_elements);
}

export const scrollToElement = function(element, speed=500) {
  $('html,body').animate({
    scrollTop: $(element).offset().top
  }, speed);
}
