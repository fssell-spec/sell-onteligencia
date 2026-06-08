from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MunicipalityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ibge_code: str | None = None
    name: str
    state: str
    population: int | None = None
    area_km2: float | None = None
    mesorregiao: str | None = None
    microrregiao: str | None = None
    region: str | None = None
    official_website: str | None = None
    transparency_url: str | None = None
    instagram_url: str | None = None
    aniversario_mes: int | None = None
    aniversario_dia: int | None = None
    created_at: datetime | None = None


class MunicipalityListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MunicipalityOut]
