import {Util, fetch} from './util.js';
import {IndexModel} from './index.js';


export const ItemCollectionModel = {
  fetch: fetch,
  urlFor: function(action, {ic_id}={}){
    let urls = {
      'index': {
        'path': `${IndexModel.urlFor('index')['path']}ic/${ic_id}`,
        'relative_path': `ic/${ic_id}`,
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
      date_item_counts: data.date_item_counts,
      date_sales: data.date_sales,
      net_sales: Util.formatToIndianRupee(data.net_sales),
      sales_delta: data.sales_delta,
      today_sales: Util.formatToIndianRupee(data.today_sales)
    }
  }
}
