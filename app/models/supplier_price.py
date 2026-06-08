from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupplierPrice(Base):
    __tablename__ = "supplier_prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    service_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    unit_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    min_price: Mapped[object | None] = mapped_column(Numeric(14, 2), nullable=True)
    avg_price: Mapped[object | None] = mapped_column(Numeric(14, 2), nullable=True)
    max_price: Mapped[object | None] = mapped_column(Numeric(14, 2), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    supplier: Mapped["Supplier"] = relationship(back_populates="prices")

    __table_args__ = (
        Index("ix_supplier_prices_supplier_id", "supplier_id"),
        Index("ix_supplier_prices_unit_type", "unit_type"),
        Index("ix_supplier_prices_avg_price", "avg_price"),
    )

    def __repr__(self) -> str:
        return f"<SupplierPrice supplier_id={self.supplier_id} avg={self.avg_price}>"
