"""fy_fields_for_org

Revision ID: ec0f15129863
Revises: 1a22f5035244
Create Date: 2017-07-12 16:43:38.148748

"""

# revision identifiers, used by Alembic.
revision = 'ec0f15129863'
down_revision = '1a22f5035244'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('organization', sa.Column('fy_start_day', sa.Integer(), nullable=True))
    op.add_column('organization', sa.Column('fy_start_month', sa.Integer(), nullable=True))
    op.add_column('organization', sa.Column('fy_timezone', sa.Unicode(255), nullable=True))
    op.create_check_constraint('org_month_check', 'organization', 'fy_start_month >= 1 and fy_start_month <= 12')
    op.create_check_constraint('org_day_check', 'organization', 'fy_start_day >= 1 and fy_start_day <= 31')


def downgrade():
    op.drop_constraint('org_day_check', 'organization')
    op.drop_constraint('org_month_check', 'organization')
    op.drop_column('organization', 'fy_timezone')
    op.drop_column('organization', 'fy_start_month')
    op.drop_column('organization', 'fy_start_day')
