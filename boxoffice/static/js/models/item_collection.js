
export const ItemCollectionModel = Backbone.Model.extend({
  url : function(id){
    return '/admin/ic/' + this.get('id');
  }
});
