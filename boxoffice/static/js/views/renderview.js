
export const renderView = function(Model, initData, viewData, template, containerId='#main-content-area'){
  if (!this.model) {
    this.model = new Model(initData);
  }
  this.model.fetch().then(function(data){
    if (!this.ractive) {
      this.ractive = new Ractive({
        el: containerId,
        // template: '#org-content-template',
        template: template,
        data: viewData
      });
    } else {
      this.ractive.render();
    }
  });
}
