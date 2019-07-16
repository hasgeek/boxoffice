"""discount coupon code unique constrain

Revision ID: 43c351227595
Revises: cdb214cf1e06
Create Date: 2019-07-15 12:49:47.211940

"""

# revision identifiers, used by Alembic.
revision = "43c351227595"
down_revision = "cdb214cf1e06"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(
        sa.DDL(
            """
                CREATE FUNCTION discount_coupon_code_validate() RETURNS TRIGGER AS $$
                DECLARE
                    code_count int;
                BEGIN
                    code_count := (SELECT COUNT(*) FROM discount_coupon
                        JOIN discount_policy ON discount_policy.id = discount_coupon.discount_policy_id
                        JOIN item_discount_policy AS item_discount_policy_1 ON discount_policy.id = item_discount_policy_1.discount_policy_id
                        JOIN item ON item.id = item_discount_policy_1.item_id
                        JOIN item_collection ON item_collection.id = item.item_collection_id
                        WHERE discount_coupon.code = NEW.code);
                    IF (code_count > 0) THEN
                        RAISE EXCEPTION 'The has already been used in this item collection';
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                CREATE TRIGGER discount_coupon_code_trigger BEFORE INSERT OR UPDATE
                ON discount_coupon
                FOR EACH ROW EXECUTE PROCEDURE discount_coupon_code_validate();
            """
        )
    )


def downgrade():
    op.execute(
        sa.DDL(
            """
            DROP TRIGGER discount_coupon_code_trigger ON discount_coupon;
            DROP FUNCTION discount_coupon_code_validate();
            """
        )
    )
