import uuid
from attr import dataclass


@dataclass(slots=True, frozen=True)
class User:
    user_id: uuid.UUID
    name: str
    surname: str
    photo_url: str
    phone_number: str
    email: str
    hashed_password_base64: str
