from flask import g
import graphene
from ..models import ItemCollection, Order


class LineItemType(graphene.ObjectType):
    id = graphene.String()
    line_item_seq = graphene.Int()
    base_amount = graphene.Float()
    discounted_amount = graphene.Float()
    final_amount = graphene.Float()
    discount_coupon_id = graphene.String()
    discount_policy_id = graphene.String()


class OrderType(graphene.ObjectType):
    id = graphene.String()
    invoice_no = graphene.Int()
    buyer_email = graphene.String()
    buyer_fullname = graphene.String()
    buyer_phone = graphene.String()
    line_items = graphene.List(LineItemType)

    def resolve_line_items(self, args, context, info):
        line_items = self.get('get_transacted_line_items') and self['get_transacted_line_items']().all()
        return [line_item.access_for(user=g.user) for line_item in line_items]


class CategoryType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    title = graphene.String()


class ItemCollectionType(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    title = graphene.String()
    categories = graphene.List(CategoryType)
    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.String())

    def resolve_categories(self, args, context, info):
        return [category.access_for(user=g.user) for category in self.categories]

    def resolve_order(self, args, context, info):
        order = Order.query.get(args.get('id'))
        return order.access_for(user=g.user)

    def resolve_orders(self, args, context, info):
        orders = self.get('get_transacted_orders') and self['get_transacted_orders']().all()
        return [order.access_for(user=g.user) for order in orders]


class QueryType(graphene.ObjectType):
    name = 'Query'
    item_collection = graphene.Field(ItemCollectionType, id=graphene.String())

    def resolve_item_collection(self, args, context, info):
        item_collection = ItemCollection.query.get(args.get('id'))
        return item_collection.access_for(user=g.user)


schema = graphene.Schema(query=QueryType)
