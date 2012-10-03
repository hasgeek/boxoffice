from decimal import Decimal
from boxoffice.models import db, BaseMixin
from boxoffice.models.event import Event
from boxoffice.models.user import User

__all__ = ['Order', 'HALF_DOZEN']

HALF_DOZEN = [
    [0, "0"],
    [1, "1"],
    [2, "2"],
    [3, "3"],
    [4, "4"],
    [5, "5"],
    [6, "6"]
]

class Order(BaseMixin, db.Model):
    """
    An Order begins with an intent to register 
    Belongs to an Event
    Contains all Attendees, Has an Owner
    """
    __tablename__ = 'order'

    #owner
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, primaryjoin=user_id == User.id,
        backref=db.backref('orders', cascade='all, delete-orphan'))

    total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.0'))

    #status -> incomplete, submitted, completed


    def update_total(self):
        self.total = sum([l.total for l in self.lineitems])

