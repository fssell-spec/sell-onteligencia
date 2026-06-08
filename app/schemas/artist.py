from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArtistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    main_style: str | None = None
    sub_style: str | None = None
    fee_tier: str | None = None
    popularity_level: str | None = None
    booking_office: str | None = None
    booking_contact: str | None = None
    origin_city: str | None = None
    origin_state: str | None = None
    official_instagram: str | None = None
    official_website: str | None = None
    notes: str | None = None
    created_at: datetime | None = None


class ArtistListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ArtistOut]
