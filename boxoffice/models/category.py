from boxoffice.models import db, BaseScopedNameMixin, Organization

__all__ = ['Category']


class Category(BaseScopedNameMixin, db.Model):
    """
    Categories are classes of items that can be purchased
    """
    __tablename__ = 'category'
    __uuid_primary_key__ = True

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship(Organization,
        backref=db.backref('category', cascade='all, delete-orphan'))

    parent = db.synonym('organization')
