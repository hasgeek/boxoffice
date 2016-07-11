
import {ItemModel} from '../models/item.js';
import {ItemTemplate} from '../templates/item.html.js';

export const ItemView = {
  render: function(item) {
    ItemModel.fetch({
      url: '/admin/item/' + item.id
    }).then(function(data){
      let ractive = new Ractive({
        el: '#main-content-area',
        template: ItemTemplate,
        data: {
          id: data.id,
          title: data.title,
          description: data.description,
          category_title: data.category_title,
          quantity_available: data.quantity_available,
          quantity_total: data.quantity_total,
          prices: data.prices,
          discount_policies: data.discount_policies
        }
      });

      ractive.on('navigate', function(event, method){
        eventBus.trigger('navigate', event.context.url);
      });
    });
  }
}
