"""change_percentage_constraint_on_discount_policy

Revision ID: 733c1e8b82e8
Revises: 6c04555d7d94
Create Date: 2018-04-24 16:19:44.855557

"""

# revision identifiers, used by Alembic.
revision = '733c1e8b82e8'
down_revision = '6c04555d7d94'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_constraint('discount_policy_percentage_check', 'discount_policy')
    op.create_check_constraint('discount_policy_percentage_check', 'discount_policy', u'percentage >= 0 and percentage <= 100')


def downgrade():
    op.drop_constraint('discount_policy_percentage_check', 'discount_policy')
    op.create_check_constraint('discount_policy_percentage_check', 'discount_policy', u'percentage > 0 and percentage <= 100')
