import {Util, Fetch} from './util.js';
import {IndexModel} from './index.js';


export const ItemCollectionModel = {
  fetch: Fetch,
  urlFor: function(action, config){
    let urls = {
      'index': {
        'path': IndexModel.urlFor('index')['path'] + 'ic/' + config.icId,
        'relativePath': 'ic/' + config.icId,
        'method': 'GET'
      }
    }
    return urls[action];
  },
  formatItems: function(items){
    var formattedItems = _.extend(items);
    formattedItems.forEach(function(item){
      item.net_sales = Util.formatToIndianRupee(item.net_sales);
    })
    return formattedItems;
  },
  formatData: function(data){
    return {
      title: data.title,
      items: this.formatItems(data.items),
      dateItemCounts: data.date_item_counts,
      dateSales: data.date_sales,
      netSales: Util.formatToIndianRupee(data.net_sales),
      salesDelta: data.sales_delta,
      todaySales: Util.formatToIndianRupee(data.today_sales)
    }
  }
}
