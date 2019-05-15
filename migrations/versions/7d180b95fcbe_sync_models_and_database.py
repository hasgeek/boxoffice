"""Sync models and database

Revision ID: 7d180b95fcbe
Revises: f78ca4cad5d6
Create Date: 2019-05-15 18:28:47.050549

"""

# revision identifiers, used by Alembic.
revision = '7d180b95fcbe'
down_revision = 'f78ca4cad5d6'

from alembic import op
import sqlalchemy as sa  # NOQA

renames = [
    ('assignee', 'assignee_line_item_current_key', 'assignee_line_item_id_current_key'),
    ('assignee', 'assignee_line_item_id', 'assignee_line_item_id_fkey'),
    ('line_item', 'line_item_id_fkey', 'line_item_previous_id_fkey'),
    ('organization', 'organization_invoicer_id_id_fkey', 'organization_invoicer_id_fkey'),
    ]


def upgrade():
    for table, oldname, newname in renames:
        op.execute(sa.DDL(
            'ALTER TABLE "{table}" RENAME CONSTRAINT "{oldname}" TO "{newname}";'.format(
                table=table, oldname=oldname, newname=newname)))

    op.create_check_constraint('category_name_check', 'category', sa.text("name <> ''"))
    op.create_unique_constraint('customer_order_access_token_key', 'customer_order', ['access_token'])
    op.drop_column('discount_coupon', 'used_at')
    op.create_check_constraint('discount_policy_name_check', 'discount_policy', sa.text("name <> ''"))
    op.alter_column('item', 'assignee_details', server_default='{}')
    op.execute(sa.DDL("UPDATE item SET assignee_details = '{}' WHERE assignee_details IS NULL;"))
    op.alter_column('item', 'assignee_details', nullable=False, existing_nullable=True)
    op.create_check_constraint('item_name_check', 'item', sa.text("name <> ''"))
    op.create_check_constraint('item_collection_name_check', 'item_collection', sa.text("name <> ''"))
    op.create_check_constraint('organization_name_check', 'organization', sa.text("name <> ''"))
    op.create_check_constraint('price_name_check', 'price', sa.text("name <> ''"))
    op.drop_index('ix_online_payment_pg_paymentid', 'online_payment')
    op.create_unique_constraint('online_payment_pg_paymentid_key', 'online_payment', ['pg_paymentid'])
    op.drop_index('ix_payment_transaction_pg_refundid', 'payment_transaction')
    op.create_unique_constraint('payment_transaction_pg_refundid_key', 'payment_transaction', ['pg_refundid'])
    op.drop_index('ix_line_item_previous_id', 'line_item')
    op.create_unique_constraint('line_item_previous_id_key', 'line_item', ['previous_id'])


def downgrade():
    op.drop_constraint('line_item_previous_id_key', 'line_item', type_='unique')
    op.create_index('ix_line_item_previous_id', 'line_item', ['previous_id'], unique=True)
    op.drop_constraint('payment_transaction_pg_refundid_key', 'payment_transaction', type_='unique')
    op.create_index('ix_payment_transaction_pg_refundid', 'payment_transaction', ['pg_refundid'], unique=True)
    op.drop_constraint('online_payment_pg_paymentid_key', 'online_payment', type_='unique')
    op.create_index('ix_online_payment_pg_paymentid', 'online_payment', ['pg_paymentid'], unique=True)
    op.drop_constraint('price_name_check', 'price', type_='check')
    op.drop_constraint('organization_name_check', 'organization', type_='check')
    op.drop_constraint('item_collection_name_check', 'item_collection', type_='check')
    op.drop_constraint('item_name_check', 'item', type_='check')
    op.alter_column('item', 'assignee_details', nullable=True, existing_nullable=False)
    op.alter_column('item', 'assignee_details', server_default=None)
    op.drop_constraint('discount_policy_name_check', 'discount_policy', type_='check')
    op.add_column('discount_coupon', sa.Column('used_at', sa.DateTime()))
    op.drop_constraint('customer_order_access_token_key', 'customer_order', type_='unique')
    op.drop_constraint('category_name_check', 'category', type_='check')

    for table, oldname, newname in reversed(renames):
        op.execute(sa.DDL(
            'ALTER TABLE "{table}" RENAME CONSTRAINT "{newname}" TO "{oldname}";'.format(
                table=table, oldname=oldname, newname=newname)))
