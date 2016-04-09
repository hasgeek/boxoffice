from datetime import datetime
from decimal import Decimal
from ..models import db, JsonDict, BaseScopedNameMixin, MarkdownColumn
from ..models import ItemCollection, Category
from ..models.discount_policy import item_discount_policy

__all__ = ['Item', 'Price']


class Item(BaseScopedNameMixin, db.Model):
    __tablename__ = 'item'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('item_collection_id', 'name'),
        db.CheckConstraint('quantity_available <= quantity_total',
            'item_quantity_available_lte_quantity_total_check'))

    description = MarkdownColumn('description', default=u'', nullable=False)

    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship(ItemCollection, backref=db.backref('items', cascade='all, delete-orphan'))
    parent = db.synonym('item_collection')

    category_id = db.Column(None, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category, backref=db.backref('items', cascade='all, delete-orphan'))

    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    discount_policies = db.relationship('DiscountPolicy', secondary=item_discount_policy, lazy='dynamic')

    assignee_details = db.Column(JsonDict, default='{}', nullable=False)

    def current_price(self):
        """
        Returns the current price for an item
        """
        return self.price_at(datetime.utcnow())

    def discounted_price(self, discount_policy):
        """
        Returns the discounted price for an item
        """
        return Price.query.filter(Price.item == self, Price.discount_policy == discount_policy).one_or_none()

    def price_at(self, timestamp):
        """
        Returns the price for an item at a given time
        """
        return Price.query.filter(Price.item == self, Price.start_at <= timestamp,
            Price.end_at > timestamp, Price.discount_policy == None).order_by('created_at desc').first()  # noqa


class Price(BaseScopedNameMixin, db.Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('item_id', 'name'),
        db.CheckConstraint('start_at < end_at', 'price_start_at_lt_end_at_check'),
        db.UniqueConstraint('item_id', 'discount_policy_id'))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('prices', cascade='all, delete-orphan'))

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=True)
    discount_policy = db.relationship('DiscountPolicy', backref=db.backref('price', cascade='all, delete-orphan'))

    parent = db.synonym('item')
    start_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)

    amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
