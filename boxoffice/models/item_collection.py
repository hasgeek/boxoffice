# -*- coding: utf-8 -*-

from ..models import db, BaseScopedNameMixin, Organization, MarkdownColumn

__all__ = ['ItemCollection']


class ItemCollection(BaseScopedNameMixin, db.Model):
    """
    Represents a collection of items or an inventory.
    """
    __tablename__ = 'item_collection'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),)

    description = MarkdownColumn('description', default=u'', nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('item_collections', cascade='all, delete-orphan'))
    parent = db.synonym('organization')
    tax_type = db.Column(db.Unicode(80), nullable=True, default=u'GST')

    __roles__ = {
        'ic_owner': {
            'read': {'id', 'name', 'title', 'description'}
        }
    }

    def roles_for(self, actor=None, anchors=()):
        roles = super(ItemCollection, self).roles_for(actor, anchors)
        if self.organization.userid in actor.organizations_owned_ids():
            roles.add('ic_owner')
        return roles

    def fetch_all_details(self):
        """
        Returns details for all the line items in a given item collection, along with the associated
        assignee (if any), discount policy (if any), discount coupon (if any), item, order and order session (if any)
        as a tuple of (keys, rows)
        """

        from ..models import Item, LineItem, Order, OrderSession, Assignee, DiscountPolicy, DiscountCoupon, LINE_ITEM_STATUS, HeadersAndDataTuple

        line_item_join = db.outerjoin(LineItem, Assignee, db.and_(LineItem.id == Assignee.line_item_id,
            Assignee.current == True)).outerjoin(DiscountCoupon,
            LineItem.discount_coupon_id == DiscountCoupon.id).outerjoin(DiscountPolicy,
            LineItem.discount_policy_id == DiscountPolicy.id).join(Item).join(Order).outerjoin(OrderSession)
        line_item_query = db.select([LineItem.id, LineItem.customer_order_id, Order.invoice_no, Item.title, LineItem.base_amount,
            LineItem.discounted_amount, LineItem.final_amount, DiscountPolicy.title, DiscountCoupon.code,
            Order.buyer_fullname, Order.buyer_email, Order.buyer_phone, Assignee.fullname,
            Assignee.email, Assignee.phone, Assignee.details, OrderSession.utm_campaign,
            OrderSession.utm_source, OrderSession.utm_medium, OrderSession.utm_term,
            OrderSession.utm_content, OrderSession.utm_id, OrderSession.gclid, OrderSession.referrer,
            Order.paid_at]).select_from(line_item_join).where(LineItem.status ==
            LINE_ITEM_STATUS.CONFIRMED).where(Order.item_collection ==
            self).order_by(LineItem.ordered_at)

        return HeadersAndDataTuple(
            ['ticket_id', 'order_id', 'receipt_no', 'ticket_type', 'base_amount', 'discounted_amount', 'final_amount', 'discount_policy', 'discount_code', 'buyer_fullname', 'buyer_email', 'buyer_phone', 'attendee_fullname', 'attendee_email', 'attendee_phone', 'attendee_details', 'utm_campaign', 'utm_source', 'utm_medium', 'utm_term', 'utm_content', 'utm_id', 'gclid', 'referrer', 'date'],
            db.session.execute(line_item_query).fetchall()
        )

    def fetch_assignee_details(self):
        """
        Return invoice_no, ticket title, assignee fullname, assignee email, assignee phone and assignee details
        for all the line items in a given item collection as a tuple of (keys, rows)
        """
        from ..models import Item, LineItem, Order, Assignee, LINE_ITEM_STATUS, HeadersAndDataTuple

        line_item_join = db.join(LineItem, Assignee, db.and_(LineItem.id == Assignee.line_item_id,
            Assignee.current == True)).join(Item).join(Order)
        line_item_query = db.select([Order.invoice_no, LineItem.line_item_seq, LineItem.id, Item.title, Assignee.fullname,
            Assignee.email, Assignee.phone, Assignee.details]).select_from(line_item_join).where(LineItem.status ==
            LINE_ITEM_STATUS.CONFIRMED).where(Order.item_collection ==
            self).order_by(LineItem.ordered_at)
        return HeadersAndDataTuple(
            ['receipt_no', 'ticket_no', 'ticket_id', 'ticket_type', 'attendee_fullname', 'attendee_email', 'attendee_phone', 'attendee_details'],
            db.session.execute(line_item_query).fetchall()
        )
