from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import OpportunityStatus, OpportunityType


class CommercialOpportunity(TimestampMixin, Base):
    __tablename__ = "commercial_opportunities"

    id: Mapped[int] = mapped_column(primary_key=True)
    municipality_id: Mapped[int] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"), nullable=False
    )
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("municipal_events.id", ondelete="SET NULL"), nullable=True
    )
    opportunity_type: Mapped[OpportunityType] = mapped_column(
        Enum(OpportunityType, name="opportunity_type_enum"), nullable=False
    )
    estimated_budget: Mapped[object | None] = mapped_column(Numeric(14, 2), nullable=True)
    estimated_event_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    urgency_score: Mapped[float | None] = mapped_column(nullable=True)
    fit_score: Mapped[float | None] = mapped_column(nullable=True)
    margin_potential_score: Mapped[float | None] = mapped_column(nullable=True)
    final_opportunity_score: Mapped[float | None] = mapped_column(nullable=True)
    recommended_artists_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    recommended_structure_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    suggested_next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OpportunityStatus] = mapped_column(
        Enum(OpportunityStatus, name="opportunity_status_enum"),
        nullable=False,
        default=OpportunityStatus.novo,
    )
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_contact_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_action_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    municipality: Mapped["Municipality"] = relationship(back_populates="opportunities")
    event: Mapped["MunicipalEvent | None"] = relationship(back_populates="opportunities")

    __table_args__ = (
        Index("ix_commercial_opportunities_municipality_id", "municipality_id"),
        Index("ix_commercial_opportunities_event_id", "event_id"),
        Index("ix_commercial_opportunities_opportunity_type", "opportunity_type"),
        Index("ix_commercial_opportunities_status", "status"),
        Index("ix_commercial_opportunities_final_score", "final_opportunity_score"),
        Index("ix_commercial_opportunities_estimated_event_date", "estimated_event_date"),
        Index("ix_commercial_opportunities_next_action_at", "next_action_at"),
    )

    def __repr__(self) -> str:
        return f"<CommercialOpportunity id={self.id} type={self.opportunity_type} status={self.status}>"
