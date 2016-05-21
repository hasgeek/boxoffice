
import {ItemCollectionModel} from '../models/item_collection.js';
import {TableTemplate, ItemCollectionTemplate} from '../templates/item_collection.html.js';

// Components
// table
// chart

let TableComponent = Ractive.extend({
  isolated: false,
  template: TableTemplate
});

export const ItemCollectionView = {
  init: function(data){
    this.ractive = new Ractive({
      el: '#main-content-area',
      template: ItemCollectionTemplate,
      data: {
        items: this.model.get('items')
      },
      components: {TableComponent: TableComponent}
    });

    this.model.on('change:items', (model, items) => this.ractive.set('items', items));

    this.ractive.on('navigate', function(event, method){
      // kill interval
      clearInterval(this.intervalId);
      eventBus.trigger('navigate', event.context.url);
    });
    window.addEventListener('popstate', (event) => {
      // kill interval
      clearInterval(this.intervalId);
    });
  },
  refresh: function(){
    this.model.fetch().then(data => this.model.set('items', data.items));
  },
  render: function(initData) {
    this.model = new ItemCollectionModel({
      id: initData.id
    });

    this.model.fetch().then(data => {
      this.model.set('items', data.items);
      this.init();
    });

    this.intervalId = setInterval(() => this.refresh(), 3000);
  }
}
