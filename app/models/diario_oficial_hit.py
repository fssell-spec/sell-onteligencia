from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class DiarioOficialHit(TimestampMixin, Base):
    __tablename__ = "diario_oficial_hits"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identificação no DO
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    data_publicacao: Mapped[str | None] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    arquivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pagina: Mapped[int | None] = mapped_column(nullable=True)
    highlight: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Extraído por LLM
    municipio_detectado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    municipio_id: Mapped[int | None] = mapped_column(
        ForeignKey("municipalities.id", ondelete="SET NULL"), nullable=True
    )
    artista_detectado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo_contratacao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_estimado: Mapped[float | None] = mapped_column(nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    # Status de acompanhamento
    status: Mapped[str] = mapped_column(String(50), default="novo", nullable=False)
    # 'novo' | 'vinculado_pncp' | 'irrelevante'

    raw_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    municipality: Mapped["Municipality | None"] = relationship(
        "Municipality", foreign_keys=[municipio_id], viewonly=True
    )

    __table_args__ = (
        UniqueConstraint("arquivo", "pagina", "keyword", name="uq_diario_arquivo_pagina_kw"),
        Index("ix_diario_hits_data", "data_publicacao"),
        Index("ix_diario_hits_municipio_id", "municipio_id"),
        Index("ix_diario_hits_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<DiarioOficialHit {self.data_publicacao} {self.artista_detectado or self.keyword}>"
