from datetime import datetime
from pydantic import BaseModel


class EventBase(BaseModel):
    trip_id: str
    destination_id: str | None = None
    title: str
    category: str | None = None
    address: str | None = None
    starts_at: datetime
    ends_at: datetime
    notes: str | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventRead(BaseModel):
    id: str
    trip_id: str
    destination_id: str | None = None
    title: str
    category: str | None = None
    address: str | None = None
    starts_at: datetime
    ends_at: datetime
    notes: str | None = None

    model_config = {"from_attributes": True}


class EventMutationResult(BaseModel):
    event: EventRead
    warnings: list[str]
