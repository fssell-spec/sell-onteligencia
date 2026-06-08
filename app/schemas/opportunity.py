from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import OpportunityStatus, OpportunityType


class OpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    municipality_id: int
    municipality_name: str | None = None
    event_id: int | None = None

    opportunity_type: OpportunityType
    status: OpportunityStatus

    estimated_budget: float | None = None
    estimated_event_date: date | None = None

    urgency_score: float | None = None
    fit_score: float | None = None
    margin_potential_score: float | None = None
    final_opportunity_score: float | None = None

    recommended_artists_json: dict[str, Any] | None = None
    recommended_structure_json: dict[str, Any] | None = None
    suggested_next_action: str | None = None

    owner: str | None = None
    last_contact_at: datetime | None = None
    next_action_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


class OpportunityListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OpportunityOut]


class OpportunityUpdate(BaseModel):
    status: OpportunityStatus | None = None
    owner: str | None = None
    suggested_next_action: str | None = None
    next_action_at: datetime | None = None
    last_contact_at: datetime | None = None
    estimated_budget: float | None = None
    estimated_event_date: date | None = None
