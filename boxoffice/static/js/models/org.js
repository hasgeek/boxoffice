
export const OrgModel = Backbone.Model.extend({
  url : function(name){
    return '/admin/o/' + this.get('name');
  }
});
