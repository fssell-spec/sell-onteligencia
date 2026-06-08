from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class AccreditationNotice(TimestampMixin, Base):
    __tablename__ = "accreditation_notices"

    id: Mapped[int] = mapped_column(primary_key=True)
    municipality_id: Mapped[int] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"), nullable=False
    )
    numero_controle: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    objeto: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor_estimado: Mapped[object | None] = mapped_column(Numeric(14, 2), nullable=True)
    data_publicacao: Mapped[object | None] = mapped_column(Date, nullable=True)
    data_encerramento: Mapped[object | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    contract_types_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    orgao_cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    orgao_nome: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    municipality: Mapped["Municipality"] = relationship(back_populates="accreditations")

    __table_args__ = (
        Index("ix_accreditation_notices_municipality_id", "municipality_id"),
        Index("ix_accreditation_notices_is_active", "is_active"),
        Index("ix_accreditation_notices_data_publicacao", "data_publicacao"),
    )

    def __repr__(self) -> str:
        return f"<AccreditationNotice id={self.id} municipio={self.municipality_id} ativo={self.is_active}>"
