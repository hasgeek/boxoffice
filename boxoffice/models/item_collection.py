from ..models import db, BaseScopedNameMixin, Organization

__all__ = ['ItemCollection']


class ItemCollection(BaseScopedNameMixin, db.Model):
    """
    Represents a collection of items or an inventory.
    """
    __tablename__ = 'item_collection'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'name'),)

    description = db.Column(db.Unicode(2500), default=u'', nullable=True)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization, backref=db.backref('item_collections', cascade='all, delete-orphan'))

    parent = db.synonym('organization')
