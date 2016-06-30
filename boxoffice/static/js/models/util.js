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

export const TableSearch = function(tableId){
  return {
    tableId : tableId,
    rowData : [],
    allMatchedIds : [],
    getRows: function(){
      return $('#' + this.tableId +' tbody tr');
    },
    setRowData: function(rowD){
      // Builds a list of objects and sets it the object's rowData
      var rowMap = [];
      $.each(this.getRows(), function(rowIndex, row){
        rowMap.push({
          'rid': '#' + $(row).attr('id'),
          'text': $(row).find('td.js-searchable').text().toLowerCase()
        });
      });
      this.rowData = rowMap;
    },
    setAllMatchedIds: function(ids){
      this.allMatchedIds = ids;
    },
    searchRows: function(q){
      // Search the rows of the table for a supplied query.
      // reset data collection on first search or if table has changed
      if (this.rowData.length !== this.getRows().length) {
        this.setRowData();
      }
      // return cached matched ids if query is blank
      if (q === '' && this.allMatchedIds.length !== 0) {
        return this.allMatchedIds;
      }
      var matchedIds = [];
      for (var i = this.rowData.length - 1; i >= 0; i--) {
        if (this.rowData[i].text.indexOf(q.toLowerCase()) !== -1) {
          matchedIds.push(this.rowData[i]['rid']);
        }
      }
      // cache ids if query is blank
      if (q === '') {
        this.setAllMatchedIds(matchedIds);
      }
      return matchedIds;
    }
  }
}
