# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from coaster.utils import LabeledEnum
from boxoffice.models import db, BaseMixin, UuidMixin, HeadersAndDataTuple, Organization, Order
from sqlalchemy import event
from sqlalchemy.sql import select, func
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm.attributes import get_history
from baseframe import __
from boxoffice.models.user import get_fiscal_year


__all__ = ['Invoice', 'INVOICE_STATUS']


class INVOICE_STATUS(LabeledEnum):
    DRAFT = (0, __("Draft"))
    FINAL = (1, __("Final"))


def gen_invoice_no(organization, jurisdiction, invoice_dt):
    """
    Generates a sequential invoice number scoped by the given organization for
    the fiscal year of the given invoice datetime
    """
    fy_start_at, fy_end_at = get_fiscal_year(jurisdiction, invoice_dt)
    return select([func.coalesce(func.max(Invoice.invoice_no + 1), 1)]).where(
        Invoice.organization == organization).where(
        Invoice.invoiced_at >= fy_start_at).where(Invoice.invoiced_at < fy_end_at)


class Invoice(UuidMixin, BaseMixin, db.Model):
    __tablename__ = 'invoice'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'invoice_no'),)

    status = db.Column(db.SmallInteger, default=INVOICE_STATUS.DRAFT, nullable=False)
    invoicee_name = db.Column(db.Unicode(255), nullable=True)
    invoicee_company = db.Column(db.Unicode(255), nullable=True)
    invoicee_email = db.Column(db.Unicode(254), nullable=True)
    invoice_no = db.Column(db.Integer(), nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    street_address_1 = db.Column(db.Unicode(255), nullable=True)
    street_address_2 = db.Column(db.Unicode(255), nullable=True)
    city = db.Column(db.Unicode(255), nullable=True)
    state = db.Column(db.Unicode(255), nullable=True)
    # ISO 3166-2 code. Eg: KA for Karnataka
    state_code = db.Column(db.Unicode(3), nullable=True)
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
        self.invoice_no = gen_invoice_no(organization, country_code, self.invoiced_at)
        super(Invoice, self).__init__(*args, **kwargs)

    @property
    def is_final(self):
        return self.status == INVOICE_STATUS.FINAL

@event.listens_for(Invoice, 'before_update')
def validate_immutable_finalized_invoice(mapper, connection, target):
    """
    Raises ValueError if a finalized invoice is being modified. Allows the status to be toggled.
    """
    # get_history helps check if the invoice was previously in draft status.
    # This check is necessary to allow edits to an invoice which may be transitioning from draft to final
    if target.is_final and get_history(target, 'status').deleted.count(INVOICE_STATUS.DRAFT) == 0:
        raise ValueError("Price-based discounts MUST have only one associated item")


def fetch_invoices(self):
    """
    Returns invoices for an organization as a tuple of (row_headers, rows)
    """
    headers = ["order_id", "receipt_no", "invoice_no", "status", "buyer_taxid", "seller_taxid", "invoicee_name", "invoicee_company",
        "invoicee_email", "street_address_1", "street_address_2", "city", "state", "state_code",
        "country_code", "postcode", "invoiced_at"]
    invoices_join = db.join(Invoice, Order)
    invoices_query = db.select([Order.id, Order.invoice_no, Invoice.invoice_no, Invoice.status,
        Invoice.buyer_taxid, Invoice.seller_taxid, Invoice.invoicee_name, Invoice.invoicee_company, Invoice.invoicee_email, Invoice.street_address_1, Invoice.street_address_2, Invoice.city,
        Invoice.state, Invoice.state_code, Invoice.country_code, Invoice.postcode, Invoice.invoiced_at
        ]).where(Invoice.organization == self).select_from(invoices_join).order_by(Invoice.invoice_no)
    return HeadersAndDataTuple(
        headers,
        db.session.execute(invoices_query).fetchall()
    )

Organization.fetch_invoices = fetch_invoices


@event.listens_for(Invoice, 'before_update')
@event.listens_for(Invoice, 'before_insert')
def validate_invoice_organization(mapper, connection, target):
    if target.organization != target.order.organization:
        raise ValueError(u"Invoice MUST be associated with the same organization as its order")
