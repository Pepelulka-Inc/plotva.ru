import uuid

from attr import dataclass


@dataclass(slots=True)
class Cart:
    entry_id: str
    product_id: uuid.UUID
    user_id: uuid.UUID
    quantity: int
