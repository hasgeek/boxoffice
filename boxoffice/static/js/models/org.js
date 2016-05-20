
export const OrgModel = Backbone.Model.extend({
  url : function(name){
    console.log(this.get('name'));
    return '/admin/o/' + this.get('name');
  }
});
