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
}

export const fetch = function (config){
  return $.ajax({
    url: config.url,
    dataType: 'json'
  });
}

export const post = function (config){
  return $.ajax({
    url: config.url,
    type: 'POST',
    dataType: 'json'
  });
}

export const scrollToElement = function (element, speed=500) {
  $('html,body').animate({
    scrollTop: $(element).offset().top
  }, speed);
}

export const getPageTitle = function (subTitle, pageTitle) {
  //Takes subTitle, pageTitle and join them into string using " — ".
  //Eg:- "Orders — JSFoo 2016"
  let newTitle = `${subTitle} — ${pageTitle}`;
  return newTitle;
}

export const completePageLoad = function (newTitle) {
  var title = $('title').html();
  //Title tag in Baseframe template is defined as "pageTitle — siteTitle"
  //Split the title tag content into pageTitle and siteTitle
  //eg:- "Orders  — JSFoo 2017 — Boxoffice" into ["Orders", "JSFoo 2016", Boxoffice"]
  var subTitles = title.split(' — ');
  var siteTitle = subTitles[subTitles.length-1];
  //Join newTitle with siteTitle
  var newPageTitle = getPageTitle(newTitle, siteTitle);
  $('title').html(newPageTitle);

  //Change progress bar status to done
  NProgress.done();
}
