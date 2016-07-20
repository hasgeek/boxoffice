import {Util, fetch} from './util.js';
import {IndexModel} from './index.js';


export const ItemCollectionModel = {
  fetch: fetch,
  getUrl: function(ic_id, relativeUrl=false){
    if(relativeUrl) {
      return '/ic/' + ic_id;
    }
    return IndexModel.url_root + '/ic/' + ic_id;
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
      date_item_counts: data.date_item_counts,
      date_sales: data.date_sales,
      net_sales: Util.formatToIndianRupee(data.net_sales),
      sales_delta: data.sales_delta,
      today_sales: Util.formatToIndianRupee(data.today_sales)
    }
  }
}
