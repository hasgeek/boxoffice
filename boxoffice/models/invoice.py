# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from boxoffice.models import db, BaseMixin, UuidMixin
from sqlalchemy import event
from sqlalchemy import sql, func
from sqlalchemy.ext.orderinglist import ordering_list
from boxoffice.models.user import get_financial_year

__all__ = ['Invoice', 'InvoiceLineItem']


def get_latest_invoice_no(organization, jurisdiction, invoice_dt):
    """
    Returns the last invoice number used, 0 if no order has been invoiced yet
    """
    query = db.session.query(sql.functions.max(Invoice.invoice_no))\
        .filter(Invoice.organization == organization)
    fy_start_at, fy_end_at = get_financial_year(jurisdiction, invoice_dt)
    if fy_start_at and fy_end_at:
        query = query.filter(Invoice.invoiced_at >= fy_start_at, Invoice.invoiced_at < fy_end_at)
    return query.scalar() or 0


class Invoice(UuidMixin, BaseMixin, db.Model):
    __tablename__ = 'invoice'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'invoice_no'),)

    invoicee_name = db.Column(db.Unicode(255), nullable=True)
    invoicee_email = db.Column(db.Unicode(254), nullable=True)
    invoice_no = db.Column(db.Integer(), nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    street_address = db.Column(db.Unicode(255), nullable=True)
    city = db.Column(db.Unicode(255), nullable=True)
    state = db.Column(db.Unicode(255), nullable=True)
    # India specific: this is the state short code. Eg: KA for Karnataka
    state_code = db.Column(db.Unicode(4), nullable=True)
    # ISO country code
    country_code = db.Column(db.Unicode(2), nullable=True)
    postcode = db.Column(db.Unicode(8), nullable=True)
    # GSTIN in the case of India
    buyer_taxid = db.Column(db.Unicode(255), nullable=True)
    seller_taxid = db.Column(db.Unicode(255), nullable=True)

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False, index=True)
    order = db.relationship('Order', backref=db.backref('invoices', cascade='all, delete-orphan'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('invoices', cascade='all, delete-orphan', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        organization = kwargs.get('organization')
        country_code = kwargs.get('country_code')
        if not country_code:
            # Default to India
            country_code = u'IN'
        if not organization:
            raise ValueError(u"Invoice MUST be initialized with an organization")
        self.invoiced_at = datetime.utcnow()
        self.invoice_no = get_latest_invoice_no(organization, country_code, self.invoiced_at) + 1
        super(Invoice, self).__init__(*args, **kwargs)


@event.listens_for(Invoice, 'before_update')
@event.listens_for(Invoice, 'before_insert')
def validate_invoice_organization(mapper, connection, target):
    if target.organization != target.order.organization:
        raise ValueError(u"Invoice MUST be associated with the same organization as its order")


class InvoiceLineItem(UuidMixin, BaseMixin, db.Model):
    __tablename__ = 'invoice_line_item'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('invoice_id', 'seq'),)

    seq = db.Column(db.Integer, nullable=False)
    item_title = db.Column(db.Unicode(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # In India, this will be GST
    tax_type = db.Column(db.Unicode(255), nullable=False)
    tax_subtype = db.Column(db.Unicode(255), nullable=False)
    discount_title = db.Column(db.Unicode(255), nullable=False)

    currency = db.Column(db.Unicode(3), nullable=False)
    base_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    discounted_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    # Total amount includes tax
    total_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)

    cgst_tax_rate = db.Column(db.Integer, nullable=True, default=0)
    sgst_tax_rate = db.Column(db.Integer, nullable=True, default=0)
    igst_tax_rate = db.Column(db.Integer, nullable=True, default=0)
    gst_compensation_cess = db.Column(db.SmallInteger, nullable=True, default=0)

    invoice_id = db.Column(None, db.ForeignKey('invoice.id'), nullable=False, index=True, unique=False)
    invoice = db.relationship(Invoice, backref=db.backref('line_items', cascade='all, delete-orphan'),
        order_by=seq, collection_class=ordering_list('seq', count_from=1))
