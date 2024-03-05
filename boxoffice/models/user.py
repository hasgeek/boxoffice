from __future__ import annotations

from typing import TYPE_CHECKING

from coaster.sqlalchemy import JsonDict
from flask_lastuser.sqlalchemy import ProfileBase, UserBase2

from . import DynamicMapped, Mapped, Model, db, relationship, sa
from .utils import HeadersAndDataTuple

__all__ = ['User', 'Organization']


class User(UserBase2, Model):
    __tablename__ = 'user'

    assignees: Mapped[list[Assignee]] = relationship(
        cascade='all, delete-orphan', back_populates='user'
    )
    orders: Mapped[list[Order]] = relationship(cascade='all, delete-orphan')

    def __repr__(self):
        """Return a representation."""
        return str(self.fullname)

    @property
    def orgs(self):
        return Organization.query.filter(
            Organization.userid.in_(self.organizations_owned_ids())
        )


class Organization(ProfileBase, Model):
    __tablename__ = 'organization'
    __table_args__ = (sa.UniqueConstraint('contact_email'),)

    # The currently used fields in details are address(html) cin (Corporate Identity
    # Number) or llpin (Limited Liability Partnership Identification Number), pan,
    # service_tax_no, support_email, logo (image url), refund_policy (html), ticket_faq
    # (html), website (url)
    details: Mapped[dict] = sa.orm.mapped_column(
        JsonDict, nullable=False, server_default=sa.text("'{}'::jsonb")
    )
    contact_email: Mapped[str] = sa.orm.mapped_column(sa.Unicode(254))
    # This is to allow organizations to have their orders invoiced by the parent
    # organization
    invoicer_id: Mapped[int | None] = sa.orm.mapped_column(
        sa.ForeignKey('organization.id')
    )
    invoicer: Mapped[Organization | None] = relationship(
        remote_side='Organization.id',
        back_populates='subsidiaries',
    )
    subsidiaries: DynamicMapped[Organization] = relationship(
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='invoicer',
    )
    menus: Mapped[list[ItemCollection]] = relationship(
        cascade='all, delete-orphan', back_populates='organization'
    )

    discount_policies: DynamicMapped[DiscountPolicy] = relationship(
        order_by='DiscountPolicy.created_at.desc()',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='organization',
    )
    invoices: DynamicMapped[Invoice] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='organization'
    )
    orders: DynamicMapped[Order] = relationship(
        cascade='all, delete-orphan', lazy='dynamic', back_populates='organization'
    )

    def permissions(self, actor, inherited=None):
        perms = super().permissions(actor, inherited)
        if self.userid in actor.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    def fetch_invoices(self):
        """Return invoices for an organization as a tuple of (row_headers, rows)."""
        from .order import Order  # pylint: disable=import-outside-toplevel

        headers = [
            'order_id',
            'receipt_no',
            'invoice_no',
            'status',
            'buyer_taxid',
            'seller_taxid',
            'invoicee_name',
            'invoicee_company',
            'invoicee_email',
            'street_address_1',
            'street_address_2',
            'city',
            'state',
            'state_code',
            'country_code',
            'postcode',
            'invoiced_at',
        ]
        invoices_query = (
            sa.select(
                Order.id,
                Order.receipt_no,
                Invoice.invoice_no,
                Invoice.status,
                Invoice.buyer_taxid,
                Invoice.seller_taxid,
                Invoice.invoicee_name,
                Invoice.invoicee_company,
                Invoice.invoicee_email,
                Invoice.street_address_1,
                Invoice.street_address_2,
                Invoice.city,
                Invoice.state,
                Invoice.state_code,
                Invoice.country_code,
                Invoice.postcode,
                Invoice.invoiced_at,
            )
            .where(Invoice.organization == self)
            .select_from(Invoice)
            .join(Order)
            .order_by(Invoice.invoice_no)
        )
        return HeadersAndDataTuple(
            headers, db.session.execute(invoices_query).fetchall()
        )


# Tail imports
from .invoice import Invoice  # isort:skip


if TYPE_CHECKING:
    from .discount_policy import DiscountPolicy
    from .item_collection import ItemCollection
    from .line_item import Assignee
    from .order import Order
