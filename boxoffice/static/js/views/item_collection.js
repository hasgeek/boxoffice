
import {ItemCollectionModel} from '../models/item_collection.js';
import {ItemCollectionTemplate} from '../templates/item_collection.html.js';

export const ItemCollectionView = {
  render: function(initData) {
    console.log(!this.ractive);
    if (!this.model) {
      this.model = new ItemCollectionModel({
        id: initData.id
      });
    }
    this.model.fetch().then(function(data){
      if (!this.ractive) {
        this.ractive = new Ractive({
          el: '#main-content-area',
          template: ItemCollectionTemplate,
          data: {
            items: data.items
          }
        });
        this.ractive.on('navigate', function(event, method){
          // console.log(event.context.url);
          eventBus.trigger('navigate', event.context.url);
        });
      } else {
        this.ractive.render();
      }
    })
  }
}
