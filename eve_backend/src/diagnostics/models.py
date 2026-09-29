from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, TimestampMixin


class Centre(TimestampMixin, Base):
    __tablename__ = "centre"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    offerings: Mapped[list["CentreTestOffering"]] = relationship(
        back_populates="centre",
        cascade="all, delete-orphan",
    )


class Test(TimestampMixin, Base):
    __tablename__ = "test"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    offerings: Mapped[list["CentreTestOffering"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
    )


class CentreTestOffering(TimestampMixin, Base):
    __tablename__ = "centre_test_offering"
    __table_args__ = (
        UniqueConstraint("centre_id", "test_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    centre_id: Mapped[UUID] = mapped_column(
        ForeignKey("centre.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_id: Mapped[UUID] = mapped_column(
        ForeignKey("test.id", ondelete="CASCADE"),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    centre: Mapped[Centre] = relationship(back_populates="offerings")
    test: Mapped[Test] = relationship(back_populates="offerings")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="offering")
