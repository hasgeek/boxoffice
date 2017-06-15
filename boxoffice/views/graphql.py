import graphene

from ..models import Category, ItemCollection, LineItem, Order


class LineItemType(graphene.ObjectType):
    id = graphene.String()
    line_item_seq = graphene.Int()
    base_amount = graphene.Float()
    discounted_amount = graphene.Float()
    final_amount = graphene.Float()


class OrderType(graphene.ObjectType):
    name = 'Order'
    id = graphene.String()
    invoice_no = graphene.Int()
    buyer_email = graphene.String()
    buyer_fullname = graphene.String()
    buyer_phone = graphene.String()
    line_items = graphene.List(LineItemType)

    def resolve_line_items(self, args, context, info):
        return self.get_transacted_line_items()


class CategoryType(graphene.ObjectType):
    name = 'Category'
    id = graphene.Int()
    name = graphene.String()
    title = graphene.String()


class ItemCollectionType(graphene.ObjectType):
    name = 'ItemCollection'
    id = graphene.String()
    name = graphene.String()
    title = graphene.String()
    categories = graphene.List(CategoryType)
    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.String())

    def resolve_categories(self, args, context, info):
        return self.categories

    def resolve_order(self, args, context, info):
        return Order.query.get(args.get('id'))

    def resolve_orders(self, args, context, info):
        return self.get_transacted_orders()


class QueryType(graphene.ObjectType):
    name = 'Query'
    item_collection = graphene.Field(ItemCollectionType, id=graphene.String())

    def resolve_item_collection(self, args, context, info):
        item_collection_id = args.get('id')
        return ItemCollection.query.get(item_collection_id)


schema = graphene.Schema(query=QueryType)
