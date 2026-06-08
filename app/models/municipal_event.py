from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import EventType


class MunicipalEvent(TimestampMixin, Base):
    __tablename__ = "municipal_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    municipality_id: Mapped[int] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type_enum"), nullable=False, default=EventType.outro
    )
    usual_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_start_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    recurrence_pattern: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    municipality: Mapped["Municipality"] = relationship(back_populates="events")
    contracts: Mapped[list["PublicContract"]] = relationship(back_populates="event")
    opportunities: Mapped[list["CommercialOpportunity"]] = relationship(
        back_populates="event"
    )

    __table_args__ = (
        Index("ix_municipal_events_municipality_id", "municipality_id"),
        Index("ix_municipal_events_event_type", "event_type"),
        Index("ix_municipal_events_usual_month", "usual_month"),
        Index("ix_municipal_events_normalized_name", "normalized_name"),
    )

    def __repr__(self) -> str:
        return f"<MunicipalEvent {self.name} ({self.event_type})>"
