from datetime import date
from pydantic import BaseModel


class TripCreate(BaseModel):
    name: str
    description: str | None = None
    startsAt: date | None = None
    endsAt: date | None = None
    visibility: str = "private"


class TripRead(BaseModel):
    id: str
    name: str
    description: str | None = None
    starts_at: date | None = None
    ends_at: date | None = None
    visibility: str

    model_config = {"from_attributes": True}
