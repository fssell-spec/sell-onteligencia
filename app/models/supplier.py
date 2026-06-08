from sqlalchemy import Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import SupplierCategory


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[SupplierCategory] = mapped_column(
        Enum(SupplierCategory, name="supplier_category_enum"),
        nullable=False,
        default=SupplierCategory.outro,
    )
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    service_region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    prices: Mapped[list["SupplierPrice"]] = relationship(back_populates="supplier")

    __table_args__ = (
        Index("ix_suppliers_name", "name"),
        Index("ix_suppliers_normalized_name", "normalized_name"),
        Index("ix_suppliers_category", "category"),
        Index("ix_suppliers_city", "city"),
        Index("ix_suppliers_state", "state"),
    )

    def __repr__(self) -> str:
        return f"<Supplier {self.name} ({self.category})>"
