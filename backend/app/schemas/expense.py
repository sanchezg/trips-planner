from datetime import date
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    trip_id: str
    destination_id: str | None = None
    event_id: str | None = None
    title: str
    category: str | None = None
    amount: float
    currency: str = "USD"
    incurred_on: date | None = None
    notes: str | None = None


class ExpenseRead(BaseModel):
    id: str
    trip_id: str
    destination_id: str | None = None
    event_id: str | None = None
    title: str
    category: str | None = None
    amount: float
    currency: str
    incurred_on: date | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}
