from pydantic import BaseModel
from typing import Optional

class UserPublicSchema(BaseModel):
    email: str
    name: str
    active: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True

