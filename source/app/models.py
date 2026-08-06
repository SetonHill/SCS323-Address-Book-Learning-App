from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    addresses: Mapped[list["Address"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    phone_numbers: Mapped[list["PhoneNumber"]] = relationship(back_populates="contact", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("char_length(trim(first_name)) > 0", name="ck_contacts_first_name"),
        CheckConstraint("char_length(trim(last_name)) > 0", name="ck_contacts_last_name"),
        Index("ix_contacts_last_first", "last_name", "first_name"),
    )


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    street: Mapped[str] = mapped_column(String(160), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    address_type: Mapped[str] = mapped_column(String(20), nullable=False)
    contact: Mapped[Contact] = relationship(back_populates="addresses")

    __table_args__ = (
        CheckConstraint("address_type IN ('home', 'work', 'other')", name="ck_addresses_type"),
        CheckConstraint("char_length(state) = 2", name="ck_addresses_state"),
        Index("ix_addresses_contact_id", "contact_id"),
    )


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_type: Mapped[str] = mapped_column(String(20), nullable=False)
    contact: Mapped[Contact] = relationship(back_populates="phone_numbers")

    __table_args__ = (
        CheckConstraint("phone_type IN ('mobile', 'home', 'work', 'other')", name="ck_phone_numbers_type"),
        Index("ix_phone_numbers_contact_id", "contact_id"),
    )
