from datetime import datetime
from boxoffice.models import db, BaseNameMixin

__all__ = ['Event']

class Event(db.Model, BaseNameMixin):
    __tablename__ = 'event'

    """
    An Event is the top level model. 
    An Item Category can exist only in relation to an Event.
    An Order can be initiated only in relation to an Event.
    """

    description = db.Column(db.Unicode(2500), default=u'', nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    short_venue = db.Column(db.Unicode(250), default=u'', nullable=True)
    venue = db.Column(db.Unicode(1200), default=u'', nullable=True)
    
    website = db.Column(db.Unicode(100), default=u'', nullable=True)
    funnel_link = db.Column(db.Unicode(250), default=u'', nullable=True)
    
    contact_name = db.Column(db.Unicode(250), default=u'', nullable=True)
    contact_email = db.Column(db.Unicode(80), default=u'', nullable=True)

    def __repr__(self):
        return self.name
