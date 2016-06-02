
export const OrdersModel = Backbone.Model.extend({
  url : function(id){
    return '/admin/ic/' + this.get('id') + '/orders';
  }
});
