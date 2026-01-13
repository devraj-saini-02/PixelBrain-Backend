from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str                             
    age: int 
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    age: int 
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class imageOut(BaseModel):
    id: int
    image_url: str
    public_id: str
    private: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class PrivateUpdate(BaseModel):
    private: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


