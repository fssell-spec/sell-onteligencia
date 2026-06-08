from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Artist(TimestampMixin, Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    main_style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sub_style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # micro=<50k | pequeno=50k-200k | medio=200k-500k | grande=>500k
    fee_tier: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # local | estadual | nacional | nacional_top
    popularity_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    booking_office: Mapped[str | None] = mapped_column(String(255), nullable=True)
    booking_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origin_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origin_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    official_instagram: Mapped[str | None] = mapped_column(String(255), nullable=True)
    official_website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    contracts: Mapped[list["PublicContract"]] = relationship(back_populates="artist")
    appearances: Mapped[list["ArtistContractAppearance"]] = relationship(
        back_populates="artist"
    )
    fees: Mapped[list["ArtistFee"]] = relationship(back_populates="artist")
    regional_strength: Mapped[list["ArtistRegionalStrength"]] = relationship(
        back_populates="artist"
    )

    __table_args__ = (
        Index("ix_artists_name", "name"),
        Index("ix_artists_normalized_name", "normalized_name"),
        Index("ix_artists_main_style", "main_style"),
        Index("ix_artists_sub_style", "sub_style"),
        Index("ix_artists_fee_tier", "fee_tier"),
        Index("ix_artists_popularity_level", "popularity_level"),
    )

    def __repr__(self) -> str:
        return f"<Artist {self.name}>"
