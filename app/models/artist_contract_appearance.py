from __future__ import annotations

import datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ArtistContractAppearance(Base):
    """Aparição confirmada de artista em contrato (PNCP) ou menção em diário oficial (DOE).

    Fonte única de verdade para cruzar artistas × municípios × valores reais.
    """

    __tablename__ = "artist_contract_appearances"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    municipality_id: Mapped[int | None] = mapped_column(
        ForeignKey("municipalities.id", ondelete="SET NULL"), nullable=True
    )
    # 'pncp' | 'doe' | 'diogrande'
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    # PK no public_contracts ou diario_oficial_hits
    source_ref_id: Mapped[int | None] = mapped_column(nullable=True)
    # Valor pago — NULL quando não consta no documento
    cache_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    event_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    publication_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    # Nome original extraído do documento antes do matching
    raw_artist_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 1.0 = match exato | 0.9 = contém | 0.7 = primeira palavra
    match_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    artist: Mapped["Artist"] = relationship(back_populates="appearances")
    municipality: Mapped["Municipality | None"] = relationship(
        back_populates="artist_appearances"
    )

    __table_args__ = (
        UniqueConstraint(
            "source", "source_ref_id", "artist_id", name="uq_aca_source_artist"
        ),
        Index("ix_aca_artist_id", "artist_id"),
        Index("ix_aca_municipality_id", "municipality_id"),
        Index("ix_aca_source_ref", "source", "source_ref_id"),
    )

    def __repr__(self) -> str:
        return f"<ArtistContractAppearance artist={self.artist_id} muni={self.municipality_id} src={self.source}>"
