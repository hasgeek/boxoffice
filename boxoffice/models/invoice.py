from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from baseframe import _
from coaster.utils import utcnow

from . import BaseMixin, Mapped, Model, UuidMixin, relationship, sa
from .enums import INVOICE_STATUS
from .utils import get_fiscal_year

__all__ = ['Invoice']


def gen_invoice_no(organization, jurisdiction, invoice_dt):
    """Generate a sequential invoice number for the organization and financial year."""
    fy_start_at, fy_end_at = get_fiscal_year(jurisdiction, invoice_dt)
    return (
        sa.select(sa.func.coalesce(sa.func.max(Invoice.invoice_no + 1), 1))
        .where(Invoice.organization == organization)
        .where(Invoice.invoiced_at >= fy_start_at)
        .where(Invoice.invoiced_at < fy_end_at)
        .scalar_subquery()
    )


class Invoice(UuidMixin, BaseMixin, Model):
    __tablename__ = 'invoice'
    __uuid_primary_key__ = True
    __table_args__ = (
        sa.UniqueConstraint(
            'organization_id', 'fy_start_at', 'fy_end_at', 'invoice_no'
        ),
    )

    status = sa.orm.mapped_column(
        sa.SmallInteger, default=INVOICE_STATUS.DRAFT, nullable=False
    )
    invoicee_name = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    invoicee_company = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    invoicee_email = sa.orm.mapped_column(sa.Unicode(254), nullable=True)
    invoice_no = sa.orm.mapped_column(sa.Integer(), nullable=True)
    fy_start_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    fy_end_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    invoiced_at = sa.orm.mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    street_address_1 = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    street_address_2 = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    city = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    state = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    # ISO 3166-2 code. Eg: KA for Karnataka
    state_code = sa.orm.mapped_column(sa.Unicode(3), nullable=True)
    # ISO country code
    country_code = sa.orm.mapped_column(sa.Unicode(2), nullable=True)
    postcode = sa.orm.mapped_column(sa.Unicode(8), nullable=True)
    # GSTIN in the case of India
    buyer_taxid = sa.orm.mapped_column(sa.Unicode(255), nullable=True)
    seller_taxid = sa.orm.mapped_column(sa.Unicode(255), nullable=True)

    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        None, sa.ForeignKey('customer_order.id'), nullable=False, index=True
    )
    order: Mapped[Order] = relationship(back_populates='invoices')

    # An invoice may be associated with a different organization as compared to its
    # order to allow for the following use case. An invoice may be issued by a parent
    # entity, while the order is booked through the child entity.
    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id'), nullable=False
    )
    organization: Mapped[Organization] = relationship(back_populates='invoices')

    __roles__ = {
        'invoicer': {
            'read': {
                'status',
                'invoicee_company',
                'invoicee_email',
                'invoice_no',
                'invoiced_at',
                'street_address_1',
                'street_address_2',
                'city',
                'state',
                'country_code',
                'postcode',
                'buyer_taxid',
                'seller_taxid',
            }
        }
    }

    def roles_for(self, actor=None, anchors=()):
        roles = super().roles_for(actor, anchors)
        if self.organization.userid in actor.organizations_owned_ids():
            roles.add('invoicer')
        return roles

    def __init__(self, *args, **kwargs):
        organization = kwargs.get('organization')
        country_code = kwargs.get('country_code')
        if not country_code:
            # Default to India
            country_code = 'IN'
        if not organization:
            raise ValueError("Invoice MUST be initialized with an organization")
        self.invoiced_at = utcnow()
        self.fy_start_at, self.fy_end_at = get_fiscal_year(
            country_code, self.invoiced_at
        )
        self.invoice_no = gen_invoice_no(organization, country_code, self.invoiced_at)
        super().__init__(*args, **kwargs)

    @property
    def is_final(self):
        return self.status == INVOICE_STATUS.FINAL

    @sa.orm.validates(
        'invoicee_name',
        'invoicee_company',
        'invoicee_email',
        'invoice_no',
        'invoiced_at',
        'street_address_1',
        'street_address_2',
        'city',
        'state',
        'state_code',
        'country_code',
        'postcode',
        'buyer_taxid',
        'seller_taxid',
        'customer_order_id',
        'organization_id',
    )
    def validate_immutable_final_invoice(self, key, val):
        if self.status == INVOICE_STATUS.FINAL:
            raise ValueError(
                _("`{attr}` cannot be modified in a finalized invoice").format(attr=key)
            )
        return val


if TYPE_CHECKING:
    from .order import Order
    from .user import Organization
