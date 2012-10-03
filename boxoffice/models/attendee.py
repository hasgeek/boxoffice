# -*- coding: utf-8 -*-
from boxoffice.models import db, BaseMixin
from boxoffice.models.event import Event
from boxoffice.models.order import Order
from uuid import uuid4
from datetime import datetime

__all__ = ['Attendee']


class Attendee(BaseMixin, db.Model):
    __tablename__ = 'attendee'

    """
    Attendees are added to an Order by its Owner
    """

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relation(Order, primaryjoin=order_id == Order.id,
        backref=db.backref('attendees', cascade='all, delete-orphan'))

    name = db.Column(db.Unicode(250), default=u'', nullable=True)
    city = db.Column(db.Unicode(250), default=u'', nullable=True)
    phone = db.Column(db.Unicode(15), default=u'', nullable=True)
    email = db.Column(db.Unicode(80), default=u'', nullable=True)
    company = db.Column(db.Unicode(250), default=u'', nullable=True)
    jobtitle = db.Column(db.Unicode(250), default=u'', nullable=True)
    twitterhandle = db.Column(db.Unicode(80), default=u'', nullable=True)