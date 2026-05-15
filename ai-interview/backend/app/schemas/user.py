from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    email: str
    nickname: str | None = None

    model_config = {"from_attributes": True}


class UserDetail(UserOut):
    created_at: datetime
    updated_at: datetime
