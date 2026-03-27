from datetime import date
from pydantic import BaseModel, Field

DEFAULT_EVENT_CATEGORIES = ["transit", "travel", "stay", "entertainment", "meal"]


class TripCreate(BaseModel):
    name: str
    description: str | None = None
    startsAt: date | None = None
    endsAt: date | None = None
    visibility: str = "private"


class TripSettingsRead(BaseModel):
    event_categories: list[str]
    calendar_auto_sync: bool

    model_config = {"from_attributes": True}


class TripSettingsUpdate(BaseModel):
    event_categories: list[str] = Field(default_factory=lambda: DEFAULT_EVENT_CATEGORIES.copy(), min_length=1)
    calendar_auto_sync: bool = False


class TripRead(BaseModel):
    id: str
    name: str
    description: str | None = None
    starts_at: date | None = None
    ends_at: date | None = None
    visibility: str
    event_categories: list[str]
    calendar_auto_sync: bool

    model_config = {"from_attributes": True}
