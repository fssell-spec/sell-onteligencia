from sqlalchemy import Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class RodeoBudgetTemplate(TimestampMixin, Base):
    __tablename__ = "rodeo_budget_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # pequeno | medio | grande
    event_size: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_audience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_items_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_rodeo_budget_templates_name", "name"),
        Index("ix_rodeo_budget_templates_event_size", "event_size"),
        Index("ix_rodeo_budget_templates_expected_audience", "expected_audience"),
    )

    def __repr__(self) -> str:
        return f"<RodeoBudgetTemplate {self.name} ({self.event_size})>"
