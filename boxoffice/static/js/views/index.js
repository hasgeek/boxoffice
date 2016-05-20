
import {IndexModel} from '../models/index.js';
import {IndexTemplate} from '../templates/index.html.js';

export const IndexView = {
  render: function() {
    console.log(!this.ractive);
    if (!this.indexModel) {
      this.indexModel = new IndexModel();
    }
    this.indexModel.fetch().then(function(data){
      if (!this.ractive) {
        console.log("ractive")
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
      } else {
        this.ractive.render();
      }
    })
  }
}
