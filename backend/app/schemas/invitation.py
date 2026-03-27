from datetime import datetime
from pydantic import BaseModel, EmailStr


class InvitationCreate(BaseModel):
    trip_id: str
    email: EmailStr
    role: str = "viewer"


class InvitationRead(BaseModel):
    id: str
    trip_id: str
    email: EmailStr
    role: str
    status: str
    token: str
    expires_at: datetime

    model_config = {"from_attributes": True}
