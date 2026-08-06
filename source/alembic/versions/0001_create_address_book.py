"""Create normalized address book tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("contacts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("first_name", sa.String(80), nullable=False), sa.Column("last_name", sa.String(80), nullable=False), sa.Column("email", sa.String(254), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.CheckConstraint("char_length(trim(first_name)) > 0", name="ck_contacts_first_name"), sa.CheckConstraint("char_length(trim(last_name)) > 0", name="ck_contacts_last_name"))
    op.create_index("ix_contacts_last_first", "contacts", ["last_name", "first_name"])
    op.create_table("addresses", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("contact_id", sa.Integer(), sa.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False), sa.Column("street", sa.String(160), nullable=False), sa.Column("city", sa.String(100), nullable=False), sa.Column("state", sa.String(2), nullable=False), sa.Column("postal_code", sa.String(10), nullable=False), sa.Column("address_type", sa.String(20), nullable=False), sa.CheckConstraint("address_type IN ('home', 'work', 'other')", name="ck_addresses_type"), sa.CheckConstraint("char_length(state) = 2", name="ck_addresses_state"))
    op.create_index("ix_addresses_contact_id", "addresses", ["contact_id"])
    op.create_table("phone_numbers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("contact_id", sa.Integer(), sa.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False), sa.Column("phone_number", sa.String(30), nullable=False), sa.Column("phone_type", sa.String(20), nullable=False), sa.CheckConstraint("phone_type IN ('mobile', 'home', 'work', 'other')", name="ck_phone_numbers_type"))
    op.create_index("ix_phone_numbers_contact_id", "phone_numbers", ["contact_id"])


def downgrade() -> None:
    op.drop_table("phone_numbers")
    op.drop_table("addresses")
    op.drop_table("contacts")
