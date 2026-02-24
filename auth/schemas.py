from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    email: str
    password: str
    name: str
    active: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

