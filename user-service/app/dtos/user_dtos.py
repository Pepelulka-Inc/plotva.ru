from typing import Optional

from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    name: str
    surname: str
    photo_url: Optional[str] = None
    phone_number: Optional[str] = None
    email: str
    hashed_password_base64: str


class UpdateUserDTO(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    photo_url: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
