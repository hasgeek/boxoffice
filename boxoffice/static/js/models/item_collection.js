import {Util} from './util.js';
import {IndexModel} from './index.js';


export const ItemCollectionModel = {
  formatItems: function (items) {
    var formattedItems = _.extend(items);
    formattedItems.forEach(function(item){
      item.net_sales = Util.formatToIndianRupee(item.net_sales);
    })
    return formattedItems;
  },
  formatData: function (data) {
    return {
      icTitle: data.title,
      items: this.formatItems(data.items),
      date_item_counts: data.date_item_counts,
      date_sales: data.date_sales,
      net_sales: Util.formatToIndianRupee(data.net_sales),
      sales_delta: data.sales_delta,
      today_sales: Util.formatToIndianRupee(data.today_sales)
    }
  }
}
