from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from baseframe import _
from coaster.utils import utcnow

from . import BaseMixin, Mapped, Model, UuidMixin, relationship, sa, timestamptz
from .enums import InvoiceStatus
from .user import Organization, User
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


class Invoice(UuidMixin, BaseMixin[UUID, User], Model):
    __tablename__ = 'invoice'
    __table_args__ = (
        sa.UniqueConstraint(
            'organization_id', 'fy_start_at', 'fy_end_at', 'invoice_no'
        ),
    )

    status: Mapped[int] = sa.orm.mapped_column(
        sa.SmallInteger, default=InvoiceStatus.DRAFT
    )
    invoicee_name: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    invoicee_company: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    invoicee_email: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(254))
    invoice_no: Mapped[int | None]
    fy_start_at: Mapped[timestamptz]
    fy_end_at: Mapped[timestamptz]
    invoiced_at: Mapped[timestamptz | None]
    street_address_1: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    street_address_2: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    city: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    state: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    # ISO 3166-2 code. Eg: KA for Karnataka
    state_code: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(3))
    # ISO country code
    country_code: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(2))
    postcode: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(8))
    # GSTIN in the case of India
    buyer_taxid: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))
    seller_taxid: Mapped[str | None] = sa.orm.mapped_column(sa.Unicode(255))

    customer_order_id: Mapped[UUID] = sa.orm.mapped_column(
        sa.ForeignKey('customer_order.id'), index=True
    )
    order: Mapped[Order] = relationship(back_populates='invoices')

    # An invoice may be associated with a different organization as compared to its
    # order to allow for the following use case. An invoice may be issued by a parent
    # entity, while the order is booked through the child entity.
    organization_id: Mapped[int] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id')
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
        return self.status == InvoiceStatus.FINAL

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
        if self.status == InvoiceStatus.FINAL:
            raise ValueError(
                _("`{attr}` cannot be modified in a finalized invoice").format(attr=key)
            )
        return val


if TYPE_CHECKING:
    from .order import Order
