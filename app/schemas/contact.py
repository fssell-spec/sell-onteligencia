from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    municipality_id: int
    name: str | None = None
    role: str | None = None
    department: str | None = None
    party: str | None = None
    email: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    instagram_url: str | None = None
    facebook_url: str | None = None
    source_url: str | None = None
    created_at: datetime | None = None
