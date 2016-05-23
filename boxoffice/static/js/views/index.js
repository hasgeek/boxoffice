
import {IndexModel} from '../models/index.js';
import {IndexTemplate} from '../templates/index.html.js';

export const IndexView = {
  render: function() {
    this.indexModel = new IndexModel();
    this.indexModel.fetch().then(function(data){
      this.ractive = new Ractive({
        el: '#main-content-area',
        template: IndexTemplate,
        data: {
          orgs: data.orgs
        }
      });
      this.ractive.on('navigate', function(event, method){
        // console.log(event.context.url);
        eventBus.trigger('navigate', event.context.url);
      });
    })
  }
}
