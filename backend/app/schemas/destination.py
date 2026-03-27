from datetime import date
from pydantic import BaseModel


class DestinationCreate(BaseModel):
    trip_id: str
    name: str
    address: str | None = None
    sort_order: int = 0
    start_date: date | None = None
    end_date: date | None = None


class DestinationRead(BaseModel):
    id: str
    trip_id: str
    name: str
    address: str | None = None
    sort_order: int
    start_date: date | None = None
    end_date: date | None = None

    model_config = {"from_attributes": True}
