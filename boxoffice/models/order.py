import itertools
from datetime import datetime
import decimal
from collections import namedtuple
from boxoffice.models import db, BaseMixin, User, Item, Price, DiscountPolicy
from coaster.utils import LabeledEnum, buid
from baseframe import __

__all__ = ['Order', 'LineItem', 'OnlinePayment', 'PaymentTransaction', 'ORDER_STATUS']


class ORDER_STATUS(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CANCELLED = (3, __("Cancelled Order"))


def get_latest_invoice_no(organization):
    """
    Returns the last invoice number used, 0 if no order has ben invoiced yet.
    """
    order = Order.query.filter_by(organization=organization,
        status=ORDER_STATUS.SALES_ORDER).order_by('created_at desc').first()
    return order.invoice_no if order else 0


class Order(BaseMixin, db.Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __tableargs__ = (db.UniqueConstraint('organization_id', 'invoice_no'),
        db.UniqueConstraint('access_token'),
        db.UniqueConstraint('item_collection_id', 'invoice_no'))

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship('ItemCollection', backref=db.backref('orders', cascade='all, delete-orphan', lazy="dynamic"))  # noqa

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('orders', cascade='all, delete-orphan', lazy="dynamic"))  # noqa

    status = db.Column(db.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)

    initiated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    access_token = db.Column(db.Unicode(22), nullable=False, default=buid)

    buyer_email = db.Column(db.Unicode(254), nullable=False)
    buyer_fullname = db.Column(db.Unicode(80), nullable=False)
    buyer_phone = db.Column(db.Unicode(16), nullable=False)

    invoice_no = db.Column(db.Integer, nullable=True)

    def confirm_sale(self):
        """Updates the status to ORDER_STATUS.SALES_ORDER"""
        self.invoice_no = get_latest_invoice_no(self.organization) + 1
        self.status = ORDER_STATUS.SALES_ORDER
        self.paid_at = datetime.utcnow()

    def invoice(self):
        """Sets invoiced_at, status"""
        self.invoiced_at = datetime.utcnow()
        self.status = ORDER_STATUS.INVOICE

    def get_amounts(self):
        """
        Calculates and returns the order's base_amount, discounted_amount and
        final_amount as a namedtuple
        """
        base_amount = (decimal.Decimal(0))
        discounted_amount = (decimal.Decimal(0))
        final_amount = (decimal.Decimal(0))
        for line_item in self.line_items:
            base_amount += line_item.base_amount
            discounted_amount += line_item.discounted_amount
            final_amount += line_item.final_amount
        order_amounts = namedtuple('OrderAmounts', ['base_amount', 'discounted_amount', 'final_amount'])
        return order_amounts(base_amount, discounted_amount, final_amount)

    # def cancel(self):
    #     """
    #     Cancels the order and all the associated line items.
    #     """
    #     for line_item in LineItem.get_confirmed(self):
    #         line_item.cancel()
    #     self.status = ORDER_STATUS.CANCELLED
    #     self.cancelled_at = datetime.utcnow()


class LINE_ITEM_STATUS(LabeledEnum):
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))


class LineItem(BaseMixin, db.Model):
    """
    Note: Line Items MUST NOT be deleted.
    They must only be cancelled.
    """
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan'))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('line_items', cascade='all, delete-orphan'))

    discount_policy_id = db.Column(None, db.ForeignKey('discount_policy.id'), nullable=True)
    discount_policy = db.relationship('DiscountPolicy', backref=db.backref('line_items'))

    discount_coupon_id = db.Column(None, db.ForeignKey('discount_coupon.id'), nullable=True)
    discount_coupon = db.relationship('DiscountCoupon', backref=db.backref('line_items'))

    base_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    status = db.Column(db.Integer, default=LINE_ITEM_STATUS.CONFIRMED, nullable=False)
    ordered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellable = db.Column(db.Boolean, nullable=False, default=True)
    transferrable = db.Column(db.Boolean, nullable=True, default=True)
    assignee_email = db.Column(db.Unicode(254), nullable=True)
    assignee_fullname = db.Column(db.Unicode(80), nullable=True)
    assignee_phone = db.Column(db.Unicode(16), nullable=True)

    @classmethod
    def make_tuple(cls, item_id, base_amount, discount_policy_id=None, discount_coupon_id=None, discount_amount=decimal.Decimal(0)):
        line_item_tup = namedtuple('LineItem', ['item_id', 'base_amount', 'discount_policy_id', 'discount_coupon_id', 'discounted_amount'])
        return line_item_tup(item_id, base_amount, discount_policy_id, discount_coupon_id, discount_amount)

    @classmethod
    def calculate(cls, line_item_dicts, coupons=[]):
        """
        Returns line item tuples with the respective base_amount, discounted_amount,
        final_amount, discount_policy and discount coupon populated
        """
        item_line_items = dict()
        line_items = []
        for line_item_dict in line_item_dicts:
            item = Item.query.get(line_item_dict.get('item_id'))
            if not item_line_items.get(unicode(item.id)):
                item_line_items[unicode(item.id)] = []
            item_line_items[unicode(item.id)].append(LineItem.make_tuple(item.id, Price.current(item).amount))
        coupon_list = list(set(coupons)) if coupons else []
        discounter = LineItemDiscounter()
        for item_id in item_line_items.keys():
            item_line_items[item_id] = discounter.get_discounted_line_items(item_line_items[item_id], coupon_list)
            line_items.extend(item_line_items[item_id])
        return line_items

    # def cancel(self):
    #     """
    #     Sets status and cancelled_at. To update the quantity
    #     create, a new line item with the required quantity
    #     """
    #     self.status = LINE_ITEM_STATUS.CANCELLED
    #     self.cancelled_at = datetime.utcnow()

    # @classmethod
    # def get_confirmed(cls, order):
    #     """
    #     Returns an order's confirmed line items.
    #     """
    #     return cls.query.filter_by(order=order, status=LINE_ITEM_STATUS.CONFIRMED).all()

    # @classmethod
    # def get_cancelled(cls, order):
    #     """
    #     Returns an order's cancelled line items.
    #     """
    #     return cls.query.filter_by(order=order, status=LINE_ITEM_STATUS.CANCELLED).all()


class LineItemDiscounter():
    def get_discounted_line_items(self, line_items, coupons=[]):
        """
        Returns line items with the maximum possible discount applied.
        """
        if not line_items:
            return None
        if len(set(line_item.item_id for line_item in line_items)) > 1:
            raise ValueError("line_items must be of the same item_id")

        valid_discounts = self.get_valid_discounts(line_items, coupons)
        if len(valid_discounts) > 1:
            # Multiple discounts found, find the combination that results
            # in the best discount
            return self.apply_max_discount(valid_discounts, line_items)
        elif len(valid_discounts) == 1:
            return self.apply_discount(valid_discounts[0], line_items)
        return line_items

    def get_valid_discounts(self, line_items, coupons):
        """
        Returns all the applicable discounts given the quantity of items
        selected and any coupons.
        """
        if not line_items:
            return None

        item = Item.query.get(line_items[0].item_id)
        if not coupons:
            return DiscountPolicy.get_from_item(item, len(line_items))
        return DiscountPolicy.get_from_item(item, len(line_items), coupons)

    def calculate_discounted_amount(self, percentage, base_amount):
        return (percentage * base_amount/decimal.Decimal(100))

    def apply_discount(self, discount, line_items, combo=False):
        """
        Returns the line_items with the given discount_policy and
        the discounted amount assigned to each line item.
        """
        should_apply_discount = True
        discounted_line_items = []
        applied_to_count = 0
        discount_obj, coupon = discount
        for line_item in line_items:
            discounted_amount = self.calculate_discounted_amount(discount_obj.percentage, line_item.base_amount)
            if should_apply_discount and (not line_item.discount_policy_id or (combo and line_item.discounted_amount < discounted_amount)):
                if coupon:
                    discounted_line_items.append(LineItem.make_tuple(line_item.item_id, line_item.base_amount, discount_obj.id, coupon.id, discounted_amount))
                else:
                    discounted_line_items.append(LineItem.make_tuple(line_item.item_id, line_item.base_amount, discount_obj.id, None, discounted_amount))
                applied_to_count += 1
                if discount_obj.item_quantity_max and applied_to_count == discount_obj.item_quantity_max:
                    # If the upper limit on the discount's allowed item quantity
                    # is reached, break out of the loop.
                    should_apply_discount = False
            else:
                # Copy the rest of the line items as they are
                discounted_line_items.append(line_item)
        return discounted_line_items

    def apply_combo_discount(self, discounts, line_items):
        """
        Applies multiple discounts to a list of line items recursively.
        """
        if len(discounts) == 0:
            return line_items
        if len(discounts) == 1:
            return self.apply_discount(discounts[0], line_items, combo=True)
        return self.apply_combo_discount([discounts[0]], self.apply_combo_discount(discounts[1:], line_items))

    def apply_max_discount(self, discounts, line_items):
        """
        Fetches the various discount combinations and applies the discount policy
        combination that results in the maximum dicount for the given list of
        line items.
        """
        discounts.extend(self.get_combos(discounts, len(line_items)))
        discounted_line_items_list = []

        for discount in discounts:
            if isinstance(discount[0], tuple):
                # Combo discount
                discounted_line_items_list.append(self.apply_combo_discount(discount, line_items))
            else:
                discounted_line_items_list.append(self.apply_discount(discount, line_items))
        return max(discounted_line_items_list,
            key=lambda line_item_list: sum([line_item.discounted_amount for line_item in line_item_list]))

    def get_combos(self, discounts, qty):
        """
        Returns the various valid discount combinations given a list of discount policies
        """
        valid_combos = []
        # Get all possible valid combinations of discounts in groups of 2..n,
        # where n is the number of discounts
        for n in range(2, len(discounts) + 1):
            combos = list(itertools.combinations(discounts, n))
            for combo in combos:
                if sum([discount.item_quantity_min for discount, coupon in combo]) <= qty:
                    # if number of line items is gte to number of items the discount policies
                    # as a combo supports, count it as a valid combo
                    valid_combos.append(combo)
        return valid_combos


class RAZORPAY_PAYMENT_STATUS(LabeledEnum):
    """
    Reflects payment statuses as specified in
    https://docs.razorpay.com/docs/return-objects
    """
    CREATED = (0, __("Created"))
    AUTHORIZED = (1, __("Authorized"))
    CAPTURED = (2, __("Captured"))
    # Only fully refunded payments.
    REFUNDED = (3, __("Refunded"))
    FAILED = (4, __("Failed"))


class OnlinePayment(BaseMixin, db.Model):
    """
    Represents payments made through a payment gateway.
    Supports Razorpay only.
    """
    __tablename__ = 'online_payment'
    __uuid_primary_key__ = True
    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('online_payments', cascade='all, delete-orphan'))

    # Payment id issued by the payment gateway
    pg_payment_id = db.Column(db.Unicode(80), nullable=False)
    # Payment status issued by the payment gateway
    pg_payment_status = db.Column(db.Integer, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    failed_at = db.Column(db.DateTime, nullable=True)

    def confirm(self):
        """
        Confirms a payment, sets confirmed_at and pg_payment_status.
        """
        self.confirmed_at = datetime.utcnow()
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.CAPTURED

    def fail(self):
        """
        Fails a payment, sets failed_at.
        """
        self.pg_payment_status = RAZORPAY_PAYMENT_STATUS.FAILED
        self.failed_at = datetime.utcnow()


class TRANSACTION_METHODS(LabeledEnum):
    ONLINE = (0, __("Online"))
    CASH = (1, __("Cash"))


class TRANSACTION_TYPES(LabeledEnum):
    PAYMENT = (0, __("Payment"))
    REFUND = (1, __("Refund"))
    # CREDIT = (2, __("Credit"))


class PaymentTransaction(BaseMixin, db.Model):
    """
    Models transactions made with a customer.
    A transaction can either be of type 'Payment', 'Refund', 'Credit',
    """
    __tablename__ = 'payment_transaction'
    __uuid_primary_key__ = True

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False)
    order = db.relationship(Order, backref=db.backref('transactions', cascade='all, delete-orphan', lazy="dynamic"))
    online_payment_id = db.Column(None, db.ForeignKey('online_payment.id'), nullable=True)
    online_payment = db.relationship(OnlinePayment, backref=db.backref('transactions', cascade='all, delete-orphan'))
    amount = db.Column(db.Numeric, default=decimal.Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
    transaction_type = db.Column(db.Integer, default=TRANSACTION_TYPES.PAYMENT, nullable=False)
    transaction_method = db.Column(db.Integer, default=TRANSACTION_METHODS.ONLINE, nullable=False)
