from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import ContractType, ProcurementModality


class PublicContract(TimestampMixin, Base):
    __tablename__ = "public_contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    municipality_id: Mapped[int | None] = mapped_column(
        ForeignKey("municipalities.id", ondelete="SET NULL"), nullable=True
    )
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("municipal_events.id", ondelete="SET NULL"), nullable=True
    )
    artist_id: Mapped[int | None] = mapped_column(
        ForeignKey("artists.id", ondelete="SET NULL"), nullable=True
    )
    contract_type: Mapped[ContractType] = mapped_column(
        Enum(ContractType, name="contract_type_enum"),
        nullable=False,
        default=ContractType.outro,
    )
    object_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_document: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contract_value: Mapped[object | None] = mapped_column(Numeric(14, 2), nullable=True)
    publication_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    event_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    process_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    procurement_modality: Mapped[ProcurementModality] = mapped_column(
        Enum(ProcurementModality, name="procurement_modality_enum"),
        nullable=False,
        default=ProcurementModality.desconhecido,
    )
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    municipality: Mapped["Municipality | None"] = relationship(back_populates="contracts")
    event: Mapped["MunicipalEvent | None"] = relationship(back_populates="contracts")
    artist: Mapped["Artist | None"] = relationship(back_populates="contracts")
    artist_fees: Mapped[list["ArtistFee"]] = relationship(back_populates="contract")

    __table_args__ = (
        Index("ix_public_contracts_municipality_id", "municipality_id"),
        Index("ix_public_contracts_event_id", "event_id"),
        Index("ix_public_contracts_artist_id", "artist_id"),
        Index("ix_public_contracts_contract_type", "contract_type"),
        Index("ix_public_contracts_publication_date", "publication_date"),
        Index("ix_public_contracts_event_date", "event_date"),
        Index("ix_public_contracts_supplier_name", "supplier_name"),
        Index("ix_public_contracts_supplier_document", "supplier_document"),
        Index("ix_public_contracts_process_number", "process_number"),
    )

    def __repr__(self) -> str:
        return f"<PublicContract id={self.id} type={self.contract_type} value={self.contract_value}>"
