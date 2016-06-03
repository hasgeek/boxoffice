
export const OrdersModel = Backbone.Model.extend({
  url : function(){
    return '/admin/ic/' + this.get('id') + '/orders';
  },
  fileUrl: function(){
    return '/admin/ic/' + this.get('id') + '/orders.csv';
  }
});
