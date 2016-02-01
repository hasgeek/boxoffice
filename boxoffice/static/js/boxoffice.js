window.Boxoffice = {};

$(function(){
  var boxoffice = window.Boxoffice;
  boxoffice.init = function(config){
    $.ajax({
      url: config.url,
      crossDomain: true,
      dataType: 'jsonp'
    }).done(function(data){
      new Ractive({
        el: 'boxoffice-widget',
        template: data.html,
        data: {
          tabs: [{
            id: 'selectItems',
            label: 'Select Tickets',
            active: true,
            complete: false,
            section: {
              categories: data.categories
            }
          },
          {
            id: 'payment',
            label: 'Payment',
            active: false,
            complete: false,
            section: {
              buyer: {
                email: '',
                fullname: '',
                phone: ''
              }
            }
          },
          {
            id: 'attendee-details',
            label: 'Attendee Details',
            active: false,
            complete: false,
            section: {
              attendees: [
              ]
            }
          }],
        }
      })
    })
  }
});