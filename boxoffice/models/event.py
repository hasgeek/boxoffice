from datetime import datetime
from boxoffice.models import db, BaseScopedNameMixin, Organization

__all__ = ['Event']


class Event(BaseScopedNameMixin, db.Model):
    """
    An Event is the top level model.
    """
    __tablename__ = 'event'
    __uuid_primary_key__ = True

    description = db.Column(db.Unicode(2500), default=u'', nullable=True)

    website = db.Column(db.Unicode(100), default=u'', nullable=True)
    funnel_link = db.Column(db.Unicode(250), default=u'', nullable=True)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization,
        backref=db.backref('events', cascade='all, delete-orphan'))

    parent = db.synonym('organization')

    def __repr__(self):
        return self.name


event_item = db.Table('event_item', db.Model.metadata,
    db.Column('event_id', None, db.ForeignKey('event.id'), primary_key=True),
    db.Column('item_id', None, db.ForeignKey('item.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False)
    )
