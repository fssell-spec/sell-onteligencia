from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ArtistFee(Base):
    __tablename__ = "artist_fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    municipality_id: Mapped[int | None] = mapped_column(
        ForeignKey("municipalities.id", ondelete="SET NULL"), nullable=True
    )
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("public_contracts.id", ondelete="SET NULL"), nullable=True
    )
    value: Mapped[object] = mapped_column(Numeric(14, 2), nullable=False)
    date: Mapped[object | None] = mapped_column(Date, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    artist: Mapped["Artist"] = relationship(back_populates="fees")
    municipality: Mapped["Municipality | None"] = relationship()
    contract: Mapped["PublicContract | None"] = relationship(back_populates="artist_fees")

    __table_args__ = (
        Index("ix_artist_fees_artist_id", "artist_id"),
        Index("ix_artist_fees_municipality_id", "municipality_id"),
        Index("ix_artist_fees_contract_id", "contract_id"),
        Index("ix_artist_fees_date", "date"),
        Index("ix_artist_fees_value", "value"),
    )

    def __repr__(self) -> str:
        return f"<ArtistFee artist_id={self.artist_id} value={self.value}>"
