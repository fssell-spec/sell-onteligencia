from sqlalchemy import DateTime, Enum, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import CrawlerStatus


class CrawlerRun(Base):
    __tablename__ = "crawler_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    crawler_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[CrawlerStatus] = mapped_column(
        Enum(CrawlerStatus, name="crawler_status_enum"),
        nullable=False,
        default=CrawlerStatus.running,
    )
    records_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_crawler_runs_crawler_name", "crawler_name"),
        Index("ix_crawler_runs_source_type", "source_type"),
        Index("ix_crawler_runs_status", "status"),
        Index("ix_crawler_runs_started_at", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<CrawlerRun {self.crawler_name} status={self.status}>"
