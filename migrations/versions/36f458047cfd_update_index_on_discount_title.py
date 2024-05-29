"""
update_index_on_discount_policy_discount_code_base.

Revision ID: 36f458047cfd
Revises: 3a585b8d5f8d
Create Date: 2017-03-16 17:04:54.849590

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '36f458047cfd'
down_revision = '3a585b8d5f8d'


def upgrade() -> None:
    op.drop_constraint(
        'discount_policy_discount_code_base_key', 'discount_policy', type_='unique'
    )
    op.create_unique_constraint(
        'discount_policy_organization_id_discount_code_base_key',
        'discount_policy',
        ['organization_id', 'discount_code_base'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'discount_policy_organization_id_discount_code_base_key',
        'discount_policy',
        type_='unique',
    )
    op.create_unique_constraint(
        'discount_policy_discount_code_base_key',
        'discount_policy',
        ['discount_code_base'],
    )
