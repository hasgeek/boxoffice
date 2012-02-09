from boxoffice.models import db, BaseNameMixin

__all__ = ['Event']

class Event(db.Model, BaseName):
    __tablename__ = 'event'
    description = db.Column(db.Text(), nullable=False)
    code = db.Column(db.Unicode(80), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.Unicode(80), nullable=False)
    

    def __repr__(self):
        return self.name
