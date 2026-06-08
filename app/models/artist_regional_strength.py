from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ArtistRegionalStrength(Base):
    __tablename__ = "artist_regional_strength"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str] = mapped_column(String(2), nullable=False, default="MS")
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    spotify_score: Mapped[float | None] = mapped_column(nullable=True)
    youtube_score: Mapped[float | None] = mapped_column(nullable=True)
    google_trends_score: Mapped[float | None] = mapped_column(nullable=True)
    public_contracts_score: Mapped[float | None] = mapped_column(nullable=True)
    final_score: Mapped[float | None] = mapped_column(nullable=True)
    calculated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    artist: Mapped["Artist"] = relationship(back_populates="regional_strength")

    __table_args__ = (
        Index("ix_artist_regional_strength_artist_id", "artist_id"),
        Index("ix_artist_regional_strength_state", "state"),
        Index("ix_artist_regional_strength_city", "city"),
        Index("ix_artist_regional_strength_final_score", "final_score"),
    )

    def __repr__(self) -> str:
        return f"<ArtistRegionalStrength artist_id={self.artist_id} state={self.state} score={self.final_score}>"
