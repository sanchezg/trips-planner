from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None

    model_config = {"from_attributes": True}
