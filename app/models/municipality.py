from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Municipality(TimestampMixin, Base):
    __tablename__ = "municipalities"

    id: Mapped[int] = mapped_column(primary_key=True)
    ibge_code: Mapped[str | None] = mapped_column(String(7), nullable=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False, default="MS")
    population: Mapped[int | None] = mapped_column(nullable=True)
    area_km2: Mapped[float | None] = mapped_column(nullable=True)
    mesorregiao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    microrregiao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    official_website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transparency_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    official_gazette_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    aniversario_mes: Mapped[int | None] = mapped_column(nullable=True)
    aniversario_dia: Mapped[int | None] = mapped_column(nullable=True)

    contacts: Mapped[list["PublicContact"]] = relationship(back_populates="municipality")
    events: Mapped[list["MunicipalEvent"]] = relationship(back_populates="municipality")
    contracts: Mapped[list["PublicContract"]] = relationship(back_populates="municipality")
    opportunities: Mapped[list["CommercialOpportunity"]] = relationship(
        back_populates="municipality"
    )
    accreditations: Mapped[list["AccreditationNotice"]] = relationship(
        back_populates="municipality"
    )
    artist_appearances: Mapped[list["ArtistContractAppearance"]] = relationship(
        back_populates="municipality"
    )

    __table_args__ = (
        UniqueConstraint("normalized_name", "state", name="uq_municipality_name_state"),
        Index("ix_municipalities_name", "name"),
        Index("ix_municipalities_normalized_name", "normalized_name"),
        Index("ix_municipalities_state", "state"),
    )

    def __repr__(self) -> str:
        return f"<Municipality {self.name}/{self.state}>"
