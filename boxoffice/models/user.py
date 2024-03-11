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
    menus: Mapped[list[Menu]] = relationship(
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

    def fetch_invoices(self, filters: dict | None = None):
        """Return invoices for an organization as a tuple of (row_headers, rows)."""
        # pylint: disable=import-outside-toplevel
        from .invoice import Invoice
        from .order import Order

        if filters is None:
            filters = {}

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
            .where(Invoice.organization_id == self.id)
            .select_from(Invoice)
            .join(Order)
            .order_by(Invoice.invoiced_at)
        )
        if 'year' in filters and 'month' in filters:
            invoices_query = invoices_query.filter(
                sa.extract('year', Invoice.invoiced_at) == filters['year']
            ).filter(sa.extract('month', Invoice.invoiced_at) == filters['month'])
        if 'from' in filters:
            invoices_query = invoices_query.filter(
                Invoice.invoiced_at >= filters['from']
            )
        if 'to' in filters:
            invoices_query = invoices_query.filter(Invoice.invoiced_at <= filters['to'])
        return HeadersAndDataTuple(
            headers, db.session.execute(invoices_query).fetchall()
        )

    def fetch_invoice_line_items(self, filters: dict | None = None):
        """
        Return invoice line items for import into Zoho Books.

        Return invoices for an organization as a tuple of (row_headers, rows) at line
        items level keeping in mind columns required for import into Zoho Books.
        """
        # pylint: disable=import-outside-toplevel
        from .invoice import Invoice
        from .line_item import LineItem
        from .order import Order

        if filters is None:
            filters = {}

        headers = [
            'Invoice Number',
            'Invoice Date',
            'Invoice Status',
            'Sales Order Number',
            'Invoice Status on Boxoffice',
            'GST Identification Number (GSTIN)',
            'Seller GSTIN',
            'Currency Code',
            # 'Place of Supply',
            'Customer Name',
            'Email',
            'invoicee_company',
            'Is Inclusive Tax',
            'Item Type',
            'Item Price',
            'Item Tax %',
            # 'Quantity',
            'Billing Address',
            'Billing Street2',
            'Billing City',
            'Billing State',
            'Billing Country',
            'Billing Code',
            'line_item_id',
            # TODO: Figure out outer join for item name
            # 'item_name',
            # TODO: Add the following fields
            # 'project',
        ]
        invoices_query = (
            sa.select(
                Invoice.invoice_no,
                Invoice.invoiced_at,
                sa.literal('DRAFT'),
                Order.id,
                Invoice.status,
                Invoice.buyer_taxid,
                Invoice.seller_taxid,
                sa.literal('INR'),
                Invoice.invoicee_name,
                Invoice.invoicee_email,
                Invoice.invoicee_company,
                sa.literal('true'),
                sa.literal('service'),
                LineItem.final_amount,
                sa.literal(18),
                # count(LineItem.id),
                Invoice.street_address_1,
                Invoice.street_address_2,
                Invoice.city,
                Invoice.state_code,
                Invoice.country_code,
                Invoice.postcode,
                LineItem.id,
                # ItemCollection.title,
            )
            .where(Invoice.organization_id == self.id)
            .select_from(Invoice)
            .join(Order)
            .join(LineItem)
            # .group_by(LineItem.id)
            # .outerjoin(
            #     ItemCollection,
            #     sa.and_(
            #         LineItem.ticket_id == Item.id,
            #         Item.menu_id == ItemCollection.id
            #     )
            # )
            .order_by(Invoice.invoiced_at)
            .order_by(Invoice.invoice_no)
        )
        if 'year' in filters and 'month' in filters:
            invoices_query = invoices_query.filter(
                sa.extract('year', Invoice.invoiced_at) == filters['year']
            ).filter(sa.extract('month', Invoice.invoiced_at) == filters['month'])
        if 'from' in filters:
            invoices_query = invoices_query.filter(
                Invoice.invoiced_at >= filters['from']
            )
        if 'to' in filters:
            invoices_query = invoices_query.filter(Invoice.invoiced_at <= filters['to'])
        return HeadersAndDataTuple(
            headers, db.session.execute(invoices_query).fetchall()
        )


# Tail imports

if TYPE_CHECKING:
    from .discount_policy import DiscountPolicy
    from .invoice import Invoice
    from .line_item import Assignee
    from .menu import Menu
    from .order import Order
